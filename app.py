from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

# أبعاد الصورة الرئيسية
WIDTH, HEIGHT = 2048, 512
BAR_HEIGHT = 100
AVATAR_SIZE = (412, 412)  # ارتفاع الصورة - الشريط العلوي

# مسارات الخطوط
FONT_TEXT_PATH = "ARIAL.TTF"
FONT_SYMBOL_PATH = "DejaVuSans.ttf"
FONT_MIXED_PATH = "NotoSans-Regular.ttf"

# تحميل الخطوط
font_nickname = ImageFont.truetype(FONT_MIXED_PATH, 130)
font_level = ImageFont.truetype(FONT_SYMBOL_PATH, 90)
font_clan = ImageFont.truetype(FONT_TEXT_PATH, 100)

# دالة جلب صورة من رابط
def fetch_image(url):
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        return Image.open(BytesIO(res.content)).convert("RGBA")
    except Exception as e:
        print(f"Error fetching image: {e}")
        return None

# توليد رابط الأيقونات
def get_icon_url(icon_id):
    return f"https://freefireinfo.vercel.app/icon?id={icon_id}"

@app.route('/bnr')
def generate_banner():
    uid = request.args.get("uid")
    region = request.args.get("region", "me")

    if not uid:
        return "UID مطلوب", 400

    try:
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

    # تحميل البنر مع الحفاظ على النسبة دون تشويه (fit ثم crop من الوسط)
    banner_orig = fetch_image(get_icon_url(banner_id))
    if not banner_orig:
        banner_img = Image.new("RGBA", (WIDTH, HEIGHT), (25, 25, 25))
    else:
        orig_ratio = banner_orig.width / banner_orig.height
        target_ratio = WIDTH / HEIGHT

        if orig_ratio > target_ratio:
            new_height = HEIGHT
            new_width = int(orig_ratio * new_height)
        else:
            new_width = WIDTH
            new_height = int(new_width / orig_ratio)

        resized = banner_orig.resize((new_width, new_height), Image.LANCZOS)
        x = (new_width - WIDTH) // 2
        y = (new_height - HEIGHT) // 2
        banner_img = resized.crop((x, y, x + WIDTH, y + HEIGHT))

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

    # كتابة DV:BNGX في منتصف الشريط الأسود
    dev_text = "DV:BNGX"
    dev_area_width = WIDTH - 512 - 40
    font_dev = ImageFont.truetype(FONT_MIXED_PATH, 60)
    bbox_dev = font_dev.getbbox(dev_text)
    w_dev = bbox_dev[2] - bbox_dev[0]
    h_dev = bbox_dev[3] - bbox_dev[1]
    dev_x = 512 + ((dev_area_width - w_dev) // 2)
    dev_y = (BAR_HEIGHT - h_dev) // 2
    draw.text((dev_x, dev_y), dev_text, font=font_dev, fill="white")

    # تحميل صورة الأفاتار بالحجم المناسب
    avatar_img = fetch_image(get_icon_url(avatar_id))
    if avatar_img:
        avatar_img = avatar_img.resize(AVATAR_SIZE, Image.LANCZOS)
        img.paste(avatar_img, (0, BAR_HEIGHT), avatar_img)

    # كتابة الاسم والكلان
    text_x = 430  # بعد الأفاتار
    draw.text((text_x, BAR_HEIGHT + 20), nickname, font=font_nickname, fill="white")
    draw.text((text_x, BAR_HEIGHT + 230), clan_name, font=font_clan, fill="white")

    # كتابة المستوى أسفل يمين الصورة
    level_text = f"Lv. {level}"
    bbox_level = font_level.getbbox(level_text)
    w_level = bbox_level[2] - bbox_level[0]
    h_level = bbox_level[3] - bbox_level[1]
    level_x = WIDTH - w_level - 50
    level_y = HEIGHT - h_level - 20
    draw.text((level_x, level_y), level_text, font=font_level, fill="white")

    # إخراج الصورة
    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')

# تشغيل الخادم
if __name__ == '__main__':
    app.run()
