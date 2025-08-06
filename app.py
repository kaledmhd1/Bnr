from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import unicodedata

app = Flask(__name__)

WIDTH, HEIGHT = 2048, 512

# المسارات للخطوط
FONT_TEXT = "ARIAL.TTF"
FONT_SYMBOLS = "DejaVuSans.ttf"  # أو "Segoe UI Symbol.ttf"

font_text_large = ImageFont.truetype(FONT_TEXT, 130)
font_text_medium = ImageFont.truetype(FONT_TEXT, 90)
font_text_level = ImageFont.truetype(FONT_TEXT, 100)
font_symbols = ImageFont.truetype(FONT_SYMBOLS, 100)

def fetch_image(url, size=None):
    res = requests.get(url)
    res.raise_for_status()
    img = Image.open(BytesIO(res.content)).convert("RGBA")
    if size:
        img = img.resize(size, Image.LANCZOS)
    return img

def is_symbol(ch):
    # يستفيد من تصنيفات Unicode للكشف عن الرموز
    cat = unicodedata.category(ch)
    return cat.startswith("S") or cat.startswith("P") or unicodedata.name(ch, "").startswith("SUPERSCRIPT")

def draw_text_mixed(draw, pos, text, font_text, font_symbols, fill):
    x, y = pos
    for ch in text:
        if is_symbol(ch):
            f = font_symbols
        else:
            f = font_text
        draw.text((x, y), ch, font=f, fill=fill)
        w, h = draw.textsize(ch, font=f)
        x += w
    return x, y

@app.route("/bnr")
def banner_image():
    uid = request.args.get("uid")
    if not uid:
        return jsonify({"error": "Missing uid"}), 400
    region = request.args.get("region", "me")
    try:
        api = f"https://razor-info.vercel.app/player-info?uid={uid}&region={region}"
        res = requests.get(api).json()
    except:
        return jsonify({"error": "API fetch failed"}), 500

    b = res.get("basicInfo", {})
    c = res.get("clanBasicInfo", {})
    nickname = b.get("nickname", "NoName")
    level = str(b.get("level", 1))
    avatar_id = b.get("headPic", 900000013)
    banner_id = b.get("bannerId", 900000014)
    pin_id = b.get("pinId")
    guild = c.get("clanName", "No Guild")

    bg_raw = fetch_image(f"https://freefireinfo.vercel.app/icon?id={banner_id}")
    avatar = fetch_image(f"https://freefireinfo.vercel.app/icon?id={avatar_id}", (512, 512))
    pin = fetch_image(f"https://freefireinfo.vercel.app/icon?id={pin_id}", (128, 128)) if pin_id else None

    if not bg_raw or not avatar:
        return jsonify({"error": "Image fetch failed"}), 500

    # تكبير الخلفية وتعبئتها
    def resize_and_crop(img, target):
        tw, th = target
        ir = img.width / img.height
        tr = tw / th
        if ir > tr:
            new_h = th
            new_w = int(ir * th)
        else:
            new_w = tw
            new_h = int(new_w / ir)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - tw)//2
        top = (new_h - th)//2
        return img.crop((left, top, left+tw, top+th))

    bg = resize_and_crop(bg_raw, (WIDTH, HEIGHT))

    final = Image.new("RGBA", (WIDTH, HEIGHT))
    final.paste(bg, (0,0))
    final.paste(avatar, (0,0), avatar)
    if pin:
        final.paste(pin, (30, HEIGHT-230), pin)

    draw = ImageDraw.Draw(final)
    bar_h = 100
    y_bar = HEIGHT - bar_h
    draw.rectangle([(512, y_bar), (WIDTH, HEIGHT)], fill=(100,100,100,230))

    # اكتشاف النص بالخطوط المختلطة
    draw_text_mixed(draw, (550, 20), nickname, font_text_large, font_symbols, fill="black")
    draw_text_mixed(draw, (550, 250), guild, font_text_medium, font_symbols, fill="black")
    draw_text_mixed(draw, (WIDTH-320, HEIGHT-230), f"Lvl. {level}", font_text_level, font_symbols, fill="black")

    buf = BytesIO()
    final.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
