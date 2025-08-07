from flask import Flask, request, send_file
from PIL import Image
from io import BytesIO
import requests

app = Flask(__name__)

# رابط الخلفية الأصلية
BACKGROUND_URL = "https://i.ibb.co/LDpHSqVY/IMG-0920.webp"

# حجم الأفاتار صغير جدًا
AVATAR_SIZE = (80, 80)  # حجم صغير جدًا

# موضع الأفاتار (مكان كلمة sayonara في المربع الأحمر)
AVATAR_POSITION = (774, 35)

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

    # جلب معلومات اللاعب للحصول على avatar_id
    try:
        api_url = f"https://razor-info.vercel.app/player-info?uid={uid}&region={region}"
        data = requests.get(api_url, timeout=5).json()
        avatar_id = data.get("basicInfo", {}).get("headPic", 900000013)
    except Exception as e:
        return f"فشل في جلب معلومات اللاعب: {e}", 500

    # تحميل الخلفية الأصلية
    bg = fetch_image(BACKGROUND_URL)
    if bg is None:
        return "فشل في تحميل الخلفية", 500

    # تحميل الأفاتار وتصغيره جدًا
    avatar = fetch_image(f"https://freefireinfo.vercel.app/icon?id={avatar_id}")
    if avatar:
        avatar = avatar.resize(AVATAR_SIZE, Image.LANCZOS)
        bg.paste(avatar, AVATAR_POSITION, avatar)

    # تجهيز الصورة للإرسال
    output = BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype="image/png")

if __name__ == "__main__":
    app.run()
