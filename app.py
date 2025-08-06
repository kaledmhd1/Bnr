from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import unicodedata

app = Flask(__name__)

WIDTH, HEIGHT = 2048, 512

FONT_TEXT_PATH = "ARIAL.TTF"
FONT_SYMBOL_PATH = "DejaVuSans.ttf"
FONT_CJK_PATH = "NotoSansCJK-Regular.otf"

font_text_large = ImageFont.truetype(FONT_TEXT_PATH, 150)
font_text_medium = ImageFont.truetype(FONT_TEXT_PATH, 90)
font_text_level = ImageFont.truetype(FONT_TEXT_PATH, 100)

font_symbol_large = ImageFont.truetype(FONT_SYMBOL_PATH, 150)
font_symbol_medium = ImageFont.truetype(FONT_SYMBOL_PATH, 90)
font_symbol_level = ImageFont.truetype(FONT_SYMBOL_PATH, 100)

font_cjk = ImageFont.truetype(FONT_CJK_PATH, 100)

def is_symbol(ch):
    cat = unicodedata.category(ch)
    # تحقق من نطاقات الحروف الكورية (Hangul)
    if 0x1100 <= ord(ch) <= 0x11FF or 0x3130 <= ord(ch) <= 0x318F or 0xAC00 <= ord(ch) <= 0xD7AF:
        return "cjk"
    if cat.startswith("S") or cat.startswith("P"):
        return "symbol"
    if "SMALL CAPITAL" in unicodedata.name(ch, ""):
        return "cjk"
    return "text"

def draw_text_mixed(draw, pos, text, fill):
    x, y = pos
    for ch in text:
        kind = is_symbol(ch)
        if kind == "text":
            # استخدم حجم الخط حسب الموقع تقريبًا
            f = font_text_large if y == 20 else (font_text_medium if y == 250 else font_text_level)
        elif kind == "symbol":
            f = font_symbol_large if y == 20 else (font_symbol_medium if y == 250 else font_symbol_level)
        else:  # cjk
            f = font_cjk
        draw.text((x, y), ch, font=f, fill=fill)
        bbox = f.getbbox(ch)
        w = bbox[2] - bbox[0]
        x += w
    return x, y

def fetch_image(url, size=None):
    try:
        res = requests.get(url)
        res.raise_for_status()
        img = Image.open(BytesIO(res.content)).convert("RGBA")
        if size:
            img = img.resize(size, Image.LANCZOS)
        return img
    except:
        return None

def get_url(icon_id):
    return f"https://freefireinfo.vercel.app/icon?id={icon_id}"

@app.route("/bnr")
def banner_image():
    uid = request.args.get("uid")
    region = request.args.get("region", "me")
    if not uid:
        return jsonify({"error": "Missing uid"}), 400

    try:
        api = f"https://razor-info.vercel.app/player-info?uid={uid}&region={region}"
        res = requests.get(api).json()
    except:
        return jsonify({"error": "API error"}), 500

    basic = res.get("basicInfo", {})
    clan = res.get("clanBasicInfo", {})

    nickname = basic.get("nickname", "NoName")
    level = basic.get("level", 1)
    avatar_id = basic.get("headPic", 900000013)
    banner_id = basic.get("bannerId", 900000014)
    pin_id = basic.get("pinId")
    guild = clan.get("clanName", "No Guild")

    bg = fetch_image(get_url(banner_id), (WIDTH, HEIGHT))
    avatar = fetch_image(get_url(avatar_id), (512, 512))
    pin = fetch_image(get_url(pin_id), (128, 128)) if pin_id else None

    if not bg or not avatar:
        return jsonify({"error": "Image load failed"}), 500

    bar_height = 100
    bar_y = HEIGHT - bar_height
    avatar_width = 512

    bg_cropped = bg.crop((0, 0, WIDTH, bar_y))
    final_img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    final_img.paste(bg_cropped, (0, 0))
    final_img.paste(avatar, (0, 0), avatar)
    if pin:
        final_img.paste(pin, (30, 384), pin)

    draw = ImageDraw.Draw(final_img)

    draw.rectangle(
        [(avatar_width, bar_y), (WIDTH, HEIGHT)],
        fill=(100, 100, 100, 230)
    )

    draw_text_mixed(draw, (avatar_width + 50, bar_y - 10), "DEV:BNGX", fill="white")
    draw_text_mixed(draw, (550, 20), nickname, fill="white")
    draw_text_mixed(draw, (550, 250), guild, fill="white")
    draw_text_mixed(draw, (WIDTH - 320, HEIGHT - 230), f"Lvl. {level}", fill="white")

    buf = BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
