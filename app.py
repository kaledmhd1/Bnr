from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

# أبعاد الصورة الرئيسية
WIDTH, HEIGHT = 2048, 512
BAR_HEIGHT = 100

# مسارات الخطوط
FONT_TEXT_PATH = "ARIAL.TTF"
FONT_SYMBOL_PATH = "DejaVuSans.ttf"
FONT_MIXED_PATH = "NotoSans-Regular.ttf"

# تحميل الخطوط
font_nickname = ImageFont.truetype(FONT_MIXED_PATH, 130)
font_level = ImageFont.truetype(FONT_SYMBOL_PATH, 90)
font_clan = ImageFont.truetype(FONT_TEXT_PATH, 100)
font_dev = ImageFont.truetype(FONT_MIXED_PATH, 60)

# دالة لجلب صورة من رابط
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

# دالة لتوليد رابط الصورة من ID
def get_icon_url(icon_id):
    return f"https://freefireinfo.vercel.app/icon?id={icon_id}"

# مسار الـ API الأساسي
@app.route('/bnr')
def generate_banner():
    uid = request.args.get("uid")
    region = request.args.get("region", "me")

    if not uid:
        return "UID مطلوب", 400

    try:
        # جلب البيانات من API
        api_url = f"https://razor-info.vercel.app/player-info?uid={uid}&region={region}"
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

    # تحميل خلفية البنر
    banner_img = fetch_image(get_icon_url(banner_id), (WIDTH, HEIGHT))
    if not banner_img:
        banner_img = Image.new("RGBA", (WIDTH, HEIGHT), (25, 25, 25))

    img = banner_img.copy()
    draw = ImageDraw.Draw(img)

    # رسم الشريط الأسود العلوي
    draw.rectangle([(0, 0), (WIDTH, BAR_HEIGHT)], fill=(0, 0, 0, 255))

    # لصق صورة bngx في الشريط
    try:
        bngx_img = Image.open("bngx.jpg.jpeg").convert("RGBA").resize((512, BAR_HEIGHT), Image.LANCZOS)
        img.paste(bngx_img, (0, 0), bngx_img)
    except Exception as e:
        print(f"Error loading bngx image: {e}")

    # كتابة DV:BNGX على يمين صورة bngx
    dev_text = "DV:BNGX"
    bbox_dev = font_dev.getbbox(dev_text)
    w_dev = bbox_dev[2] - bbox_dev[0]
    h_dev = bbox_dev[3] - bbox_dev[1]
    dev_x = 512 + 20
    dev_y = (BAR_HEIGHT - h_dev) // 2
    draw.text((dev_x, dev_y), dev_text, font=font_dev, fill="white")

    # تحميل صورة الأفاتار
    avatar_img = fetch_image(get_icon_url(avatar_id), (512, 512))
    if avatar_img:
        img.paste(avatar_img, (0, BAR_HEIGHT), avatar_img)

    # الكتابة على يمين الأفاتار
    text_x = 550
    nickname_y = BAR_HEIGHT + 20
    clan_y = BAR_HEIGHT + 300

    draw.text((text_x, nickname_y), nickname, font=font_nickname, fill="white")

    # حساب حجم نص المستوى
    level_text = f"Lv. {level}"
    bbox_level = font_level.getbbox(level_text)
    w_level = bbox_level[2] - bbox_level[0]
    draw.text((WIDTH - w_level - 50, nickname_y), level_text, font=font_level, fill="white")

    draw.text((text_x, clan_y), clan_name, font=font_clan, fill="white")

    # إخراج الصورة
    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')

if __name__ == '__main__':
    app.run()
