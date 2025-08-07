from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

AVATAR_SIZE = (125, 125)
FONT_PATH = "Tajawal-Bold.ttf"
SECRET_KEY = "BNGX"  # ← مفتاح التحقق

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

@app.route('/bnr')
def generate_avatar_only():
    uid = request.args.get("uid")
    key = request.args.get("key")

    # تحقق من المفتاح
    if key != SECRET_KEY:
        return "🚫 مفتاح غير صحيح", 403

    if not uid:
        return "يرجى تحديد UID", 400

    try:
        api_url = f"https://infoplayerbngx.vercel.app/get?uid={uid}"
        res = requests.get(api_url, timeout=5).json()
        avatar_id = res["captainBasicInfo"]["headPic"]
        nickname = res["captainBasicInfo"]["nickname"]
        likes = res["captainBasicInfo"]["liked"]
        level = res["captainBasicInfo"]["level"]
    except Exception as e:
        return f"❌ فشل في جلب البيانات: {e}", 500

    bg_img = fetch_image("https://i.postimg.cc/L4PQBgmx/IMG-20250807-042134-670.jpg")
    if not bg_img:
        return "❌ فشل في تحميل الخلفية", 500

    img = bg_img.copy()
    draw = ImageDraw.Draw(img)

    # إعداد الخطوط
    font_size_uid = 35
    font_size_nickname = 50
    font_size_likes = 40
    font_size_dev = 30

    try:
        font_uid = ImageFont.truetype(FONT_PATH, font_size_uid)
        font_nickname = ImageFont.truetype(FONT_PATH, font_size_nickname)
        font_likes = ImageFont.truetype(FONT_PATH, font_size_likes)
        font_dev = ImageFont.truetype(FONT_PATH, font_size_dev)
    except Exception:
        font_uid = ImageFont.load_default()
        font_nickname = ImageFont.load_default()
        font_likes = ImageFont.load_default()
        font_dev = ImageFont.load_default()

    # تحميل الأفاتار
    avatar_img = fetch_image(f"https://freefireinfo.vercel.app/icon?id={avatar_id}", AVATAR_SIZE)
    avatar_x = 90
    avatar_y = 82
    if avatar_img:
        img.paste(avatar_img, (avatar_x, avatar_y), avatar_img)

    # ✳️ رسم اللفل تحت الأفاتار
    level_text = f"Lv. {level}"
    bbox_level = font_nickname.getbbox(level_text)
    level_w = bbox_level[2] - bbox_level[0]
    level_h = bbox_level[3] - bbox_level[1]
    level_x = avatar_x - 40
    level_y = avatar_y + 160
    draw.text((level_x, level_y), level_text, font=font_nickname, fill="black")

    # رسم الاسم يمين الأفاتار
    nickname_x = avatar_x + AVATAR_SIZE[0] + 80
    nickname_y = avatar_y - 3
    draw.text((nickname_x, nickname_y), nickname, font=font_nickname, fill="black")

    # رسم UID في أسفل يمين الصورة
    text = uid
    bbox_uid = font_uid.getbbox(text)
    text_w = bbox_uid[2] - bbox_uid[0]
    text_h = bbox_uid[3] - bbox_uid[1]
    img_w, img_h = img.size

    text_x = img_w - text_w - 110
    text_y = img_h - text_h - 17
    draw.text((text_x, text_y), text, font=font_uid, fill="white")

    # رسم عدد اللايكات فوق UID
    likes_text = f"{likes} ❤️"
    bbox_likes = font_likes.getbbox(likes_text)
    likes_w = bbox_likes[2] - bbox_likes[0]
    likes_h = bbox_likes[3] - bbox_likes[1]

    likes_x = img_w - likes_w - 60
    likes_y = text_y - likes_h - 25
    draw.text((likes_x, likes_y), likes_text, font=font_likes, fill="black")

    # ✳️ إضافة DEV BY : BNGX في الزاوية العليا اليمنى
    dev_text = "DEV BY : BNGX"
    bbox_dev = font_dev.getbbox(dev_text)
    dev_w = bbox_dev[2] - bbox_dev[0]
    dev_h = bbox_dev[3] - bbox_dev[1]
    padding = 30
    dev_x = img_w - dev_w - padding
    dev_y = padding
    draw.text((dev_x, dev_y), dev_text, font=font_dev, fill="white")

    # إرسال الصورة
    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')

if __name__ == '__main__':
    app.run()
