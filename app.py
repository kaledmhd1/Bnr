from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

# إعدادات الصورة
WIDTH, HEIGHT = 2048, 512
FONT_PATH = "ARIAL.TTF"
font_nickname = ImageFont.truetype(FONT_PATH, 130)  # خط أكبر لاسم اللاعب فقط
font_large = ImageFont.truetype(FONT_PATH, 90)     # حجم افتراضي للكلان و DEV:BNGX
font_level = ImageFont.truetype(FONT_PATH, 75)     # حجم اللفل

# دالة جلب الصور
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

# دالة توليد رابط الأيقونة
def get_url(icon_id):
    return f"https://freefireinfo.vercel.app/icon?id={icon_id}"

@app.route("/bnr")
def banner_image():
    uid = request.args.get("uid")
    if not uid:
        return jsonify({"error": "Thiếu uid"}), 400

    region = "me"  # نجبر دائمًا على "me"

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

    bg.paste(avatar, (0, 0), avatar)
    if pin:
        bg.paste(pin, (30, 384), pin)

    draw = ImageDraw.Draw(bg)
    draw.text((550, 20), nickname, font=font_nickname, fill="white")  # اسم اللاعب بخط أكبر
    draw.text((550, 350), guild, font=font_large, fill="white")       # حجم افتراضي للكلان
    draw.text((WIDTH - 260, HEIGHT - 200), f"Lvl. {level}", font=font_level, fill="white")
    draw.text((WIDTH - 460, HEIGHT - 90), "DEV:BNGX", font=font_large, fill="white")

    buf = BytesIO()
    bg.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
