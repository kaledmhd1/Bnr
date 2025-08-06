from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

WIDTH, HEIGHT = 2048, 512
FONT_PATH = "ARIAL.TTF"

font_nickname = ImageFont.truetype(FONT_PATH, 150)
font_large = ImageFont.truetype(FONT_PATH, 90)
font_level = ImageFont.truetype(FONT_PATH, 100)

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
    if not uid:
        return jsonify({"error": "Thiếu uid"}), 400

    region = "me"

    try:
        api = f"https://razor-info.vercel.app/player-info?uid={uid}&region={region}"
        res = requests.get(api).json()
    except:
        return jsonify({"error": "Không thể lấy dữ liệu từ API"}), 500

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
        return jsonify({"error": "Không tải được ảnh"}), 500

    bar_height = 100
    bar_y = HEIGHT - bar_height
    avatar_width = 512

    # اقتصاص الخلفية من الأعلى حتى بداية الشريط الرصاصي
    bg_cropped = bg.crop((0, 0, WIDTH, bar_y))

    # إنشاء صورة جديدة بحجم كامل البنر
    final_img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))

    # لصق الخلفية المقتصة في الأعلى
    final_img.paste(bg_cropped, (0, 0))

    # لصق الأفاتار والصور الأخرى
    final_img.paste(avatar, (0, 0), avatar)
    if pin:
        final_img.paste(pin, (30, 384), pin)

    draw = ImageDraw.Draw(final_img)

    # رسم الشريط الرصاصي في الأسفل
    draw.rectangle(
        [(avatar_width, bar_y), (WIDTH, HEIGHT)],
        fill=(100, 100, 100, 230)
    )

    # كتابة DEV:BNGX في وسط الشريط الرمادي
    dev_text = "DEV:BNGX"
    text_bbox = font_large.getbbox(dev_text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = avatar_width + (WIDTH - avatar_width - text_width) // 15
    text_y = bar_y - 27
    draw.text((text_x, text_y), dev_text, font=font_large, fill="white")

    # كتابة النصوص الأخرى فوق الخلفية والصور
    draw.text((550, 20), nickname, font=font_nickname, fill="white")
    draw.text((550, 250), guild, font=font_large, fill="white")
    draw.text((WIDTH - 320, HEIGHT - 230), f"Lvl. {level}", font=font_level, fill="white")

    buf = BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
