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
font_dev = ImageFont.truetype(FONT_MIXED_PATH, 45)

def fetch_image(url, size=None):
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        img = Image.open(BytesIO(res.content)).convert("RGBA")
        if size:
            img = img.resize(size, Image.LANCZOS)
        return img
    except:
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
        # استدعاء API الجديد
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

    # إنشاء صورة البنر
    img = Image.new("RGBA", (WIDTH, HEIGHT), (25, 25, 25))
    draw = ImageDraw.Draw(img)

    # الشريط الرمادي
    draw.rectangle([(500, 0), (WIDTH, HEIGHT)], fill=(40, 40, 40))

    # تحميل الصورة الأفاتار (headPic)
    avatar_img = fetch_image(get_icon_url(avatar_id), (512, 512))
    if avatar_img:
        img.paste(avatar_img, (0, 0), avatar_img)

    # كتابة البيانات
    draw.text((550, 90), nickname, font=font_nickname, fill="white")
    draw.text((550, 260), f"Lv. {level}", font=font_level, fill="white")
    draw.text((550, 360), clan_name, font=font_clan, fill="white")
    draw.text((1900, 10), "DV:B𝙽𝙂𝚇", font=font_dev, fill="white")

    # إخراج الصورة
    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')

if __name__ == '__main__':
    app.run()
