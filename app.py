from flask import Flask, request, send_file
from PIL import Image, ImageDraw
from io import BytesIO
import requests

app = Flask(__name__)

AVATAR_SIZE = (60, 60)  # آفاتار صغير جداً

def fetch_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        print(f"خطأ في جلب الصورة: {e}")
    return None

@app.route("/bnr")
def generate_banner():
    uid = request.args.get("uid")
    region = request.args.get("region")

    # خلفية المستخدم (بحجمها الأصلي)
    background_url = "https://i.ibb.co/LDpHSqVY/IMG-0920.webp"
    background = fetch_image(background_url)
    if background is None:
        return "فشل في تحميل الخلفية", 400

    # آفاتار اللاعب
    avatar_url = f"https://freefireinfo.vercel.app/icon?id=900000013"
    avatar = fetch_image(avatar_url)
    if avatar is None:
        return "فشل في تحميل صورة الآفاتار", 400

    # تصغير الآفاتار
    avatar = avatar.resize(AVATAR_SIZE)

    # وضع الآفاتار مكان المربع الأحمر (تعديل هذه الإحداثيات حسب مكانه)
    avatar_x = 670
    avatar_y = 110
    background.paste(avatar, (avatar_x, avatar_y), avatar)

    # تجهيز الصورة للإرسال
    output = BytesIO()
    background.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
