from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

WIDTH, HEIGHT = 2048, 512
FONT_TEXT_PATH = "ARIAL.TTF"
FONT_SYMBOL_PATH = "DejaVuSans.ttf"
FONT_MIXED_PATH = "NotoSans-Regular.ttf"

font_nickname = ImageFont.truetype(FONT_MIXED_PATH, 130)
font_level = ImageFont.truetype(FONT_SYMBOL_PATH, 90)
font_clan = ImageFont.truetype(FONT_TEXT_PATH, 100)
font_dev = ImageFont.truetype(FONT_MIXED_PATH, 60)  # حجم أكبر للنص

def fetch_image(url, size=None):
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        img = Image.open(BytesIO(res.content)).convert("RGBA")
        if size:
            img = img.resize(size, Image.LANCZOS)
        return img
    except Exception as e:
        print(f"Error fetching image: {e}")
        return None

def get_icon_url(icon_id):
    return f"https://freefireinfo.vercel.app/icon?id={icon_id}"

@app.route('/bnr')
def generate_banner():
    uid = request.args.get("uid")
    region = request.args.get("region", "me")

    if not uid:
        return "UID مطلوب", 400

    try:
        api_url = f"https://razor-info.vercel.app/player-info?uid={uid}&region=me"
        res = requests.get(api_url, timeout=5).json()

        basic = res.get("basicInfo", {})
        clan = res.get("clanBasicInfo", {})

        nickname = basic.get("nickname", "NoName")
        level = basic.get("level", 1)
        avatar_id = basic.get("headPic", 900000013)
        banner_id = basic.get("bannerId", 900000014)
        clan_name = clan.get("clanName", "No Clan")

    except Exception as e:
        return f"❌ فشل في جلب البيانات: {e}", 500

    # تحميل صورة البنر كخلفية
    banner_img = fetch_image(get_icon_url(banner_id), (WIDTH, HEIGHT))
    if not banner_img:
        # لو فشل التحميل، نستخدم خلفية داكنة عادية
        banner_img = Image.new("RGBA", (WIDTH, HEIGHT), (25, 25, 25))

    img = banner_img.copy()
    draw = ImageDraw.Draw(img)

    # تحميل صورة الأفاتار
    avatar_img = fetch_image(get_icon_url(avatar_id), (512, 512))
    if avatar_img:
        img.paste(avatar_img, (0, 0), avatar_img)

    # رسم الشريط الرمادي في الأسفل (ارتفاع 100 بكسل)
    bar_height = 100
    bar_y = HEIGHT - bar_height
    draw.rectangle([(500, bar_y), (WIDTH, HEIGHT)], fill=(40, 40, 40, 255))

    # كتابة النصوص فوق الصورة والشريط الرمادي
    draw.text((550, 90), nickname, font=font_nickname, fill="white")
    draw.text((550, 260), f"Lv. {level}", font=font_level, fill="white")
    draw.text((550, 360), clan_name, font=font_clan, fill="white")

    # كتابة DV:BNGX في منتصف الشريط الرمادي السفلي
    dev_text = "DV:BNGX"
    w, h = draw.textsize(dev_text, font=font_dev)
    dev_x = 500 + (WIDTH - 500 - w) // 2
    dev_y = bar_y + (bar_height - h) // 2
    draw.text((dev_x, dev_y), dev_text, font=font_dev, fill="white")

    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')

if __name__ == '__main__':
    app.run()
