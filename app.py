from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

# أبعاد الصورة الرئيسية
WIDTH, HEIGHT = 2048, 512
BAR_HEIGHT = 100
AVATAR_SIZE = (512, 412)

# مسارات الخطوط
FONT_TEXT_PATH = "ARIAL.TTF"
FONT_SYMBOL_PATH = "DejaVuSans.ttf"
FONT_MIXED_PATH = "NotoSans-Regular.ttf"

# تحميل الخطوط
font_nickname = ImageFont.truetype(FONT_MIXED_PATH, 130)
font_level = ImageFont.truetype(FONT_SYMBOL_PATH, 90)
font_clan = ImageFont.truetype(FONT_TEXT_PATH, 100)

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

    # إنشاء صورة فارغة للخلفية
    banner_img_full = fetch_image(get_icon_url(banner_id))
    banner_img = Image.new("RGBA", (WIDTH, HEIGHT), (25, 25, 25))
    if banner_img_full:
        banner_part = banner_img_full.resize((WIDTH - 512, HEIGHT), Image.LANCZOS)
        banner_img.paste(banner_part, (512, 0))

    img = banner_img.copy()
    draw = ImageDraw.Draw(img)

    # الشريط الأسود العلوي
    draw.rectangle([(0, 0), (WIDTH, BAR_HEIGHT)], fill=(0, 0, 0, 255))

    # bngx في الشريط
    try:
        bngx_img = Image.open("bngx.jpg.jpeg").convert("RGBA").resize((512, BAR_HEIGHT), Image.LANCZOS)
        img.paste(bngx_img, (0, 0), bngx_img)
    except Exception as e:
        print(f"Error loading bngx image: {e}")

    # كتابة DV:BNGX بعد صورة bngx
    dev_text = "DV:BNGX"
    font_dev = ImageFont.truetype(FONT_MIXED_PATH, 80)
    text_start_x = 512 + 20
    text_y = (BAR_HEIGHT - font_dev.getbbox(dev_text)[3]) // 2
    draw.text((text_start_x, text_y), dev_text, font=font_dev, fill="white")

    # الأفاتار
    avatar_img = fetch_image(get_icon_url(avatar_id), AVATAR_SIZE)
    if avatar_img:
        img.paste(avatar_img, (0, BAR_HEIGHT), avatar_img)

    # الاسم والكلان
    text_x = 530
    draw.text((text_x, BAR_HEIGHT + 20), nickname, font=font_nickname, fill="white")
    draw.text((text_x, BAR_HEIGHT + 230), clan_name, font=font_clan, fill="white")

    # المستوى
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

if __name__ == '__main__':
    app.run()
