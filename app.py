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

# دالة جلب صورة من رابط
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

# توليد رابط الأيقونات
def get_icon_url(icon_id):
    return f"https://freefireinfo.vercel.app/icon?id={icon_id}"

# دالة لتكبير الخط لملء مساحة معينة
def get_fitted_font(text, font_path, max_width, max_height, start_size=10):
    font_size = start_size
    while True:
        font = ImageFont.truetype(font_path, font_size)
        bbox = font.getbbox(text)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if w >= max_width or h >= max_height:
            break
        font_size += 1
    return ImageFont.truetype(font_path, font_size - 1)

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

    # كتابة DV:BNGX بحجم 60 وبمنتصف الشريط الأسود
    dev_text = "DV:BNGX"
    dev_area_width = WIDTH - 512 - 40  # المساحة بعد bngx مع بعض الهوامش
    font_dev = ImageFont.truetype(FONT_MIXED_PATH, 60)

    bbox_dev = font_dev.getbbox(dev_text)
    w_dev = bbox_dev[2] - bbox_dev[0]
    h_dev = bbox_dev[3] - bbox_dev[1]

    dev_x = 512 + ((dev_area_width - w_dev) // 2)
    dev_y = (BAR_HEIGHT - h_dev) // 2  # وسط عموديًا داخل الشريط

    draw.text((dev_x, dev_y), dev_text, font=font_dev, fill="white")

    # تحميل صورة الأفاتار
    avatar_img = fetch_image(get_icon_url(avatar_id), (512, 512))
    if avatar_img:
        img.paste(avatar_img, (0, BAR_HEIGHT), avatar_img)

    # كتابة الاسم والكلان
    text_x = 550
    draw.text((text_x, BAR_HEIGHT + 20), nickname, font=font_nickname, fill="white")
    draw.text((text_x, BAR_HEIGHT + 300), clan_name, font=font_clan, fill="white")

    # كتابة المستوى أسفل يمين الصورة
    level_text = f"Lv. {level}"
    bbox_level = font_level.getbbox(level_text)
    w_level = bbox_level[2] - bbox_level[0]
    h_level = bbox_level[3] - bbox_level[1]
    level_x = WIDTH - w_level - 50
    level_y = HEIGHT - h_level - 20
    draw.text((level_x, level_y), level_text, font=font_level, fill="white")
    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')
# تصحيح شرط التشغيل
if __name__ == '__main__':
    app.run()
