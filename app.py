from flask import Flask, request, send_file
from PIL import Image
from io import BytesIO
import requests

app = Flask(__name__)

BACKGROUND_URL = "https://i.ibb.co/LDpHSqVY/IMG-0920.webp"

# إحداثيات المربع الأحمر في الصورة الأصلية (التي فيها "sayonara")
AVATAR_POSITION = (774, 35)  # (x, y) — وسط المربع الأحمر
AVATAR_SIZE = (180, 180)     # حجم الأفاتار ليغطي المربع الأحمر

def fetch_image(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        print(f"فشل في جلب الصورة: {e}")
        return None

@app.route("/bnr")
def generate_banner():
    uid = request.args.get("uid")
    region = request.args.get("region", "me")

    if not uid:
        return "يرجى إدخال uid", 400

    # جلب معلومات اللاعب
    try:
        api_url = f"https://razor-info.vercel.app/player-info?uid={uid}&region={region}"
        data = requests.get(api_url, timeout=5).json()
        avatar_id = data.get("basicInfo", {}).get("headPic", 900000013)
    except Exception as e:
        return f"فشل في جلب معلومات اللاعب: {e}", 500

    # تحميل صورة الخلفية الأصلية كما هي
    bg = fetch_image(BACKGROUND_URL)
    if bg is None:
        return "فشل في تحميل الخلفية", 500

    # تحميل صورة الأفاتار
    avatar = fetch_image(f"https://freefireinfo.vercel.app/icon?id={avatar_id}")
    if avatar:
        avatar = avatar.resize(AVATAR_SIZE, Image.LANCZOS)
        bg.paste(avatar, AVATAR_POSITION, avatar)

    # إخراج الصورة النهائية
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype="image/png")

if __name__ == "__main__":
    app.run()
