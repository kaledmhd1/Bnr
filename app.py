from flask import Flask, request, send_file
from PIL import Image
from io import BytesIO
import requests

app = Flask(__name__)

BACKGROUND_IMAGE_URL = "https://i.ibb.co/LDpHSqVY/IMG-0920.webp"

def fetch_image(url):
    try:
        print(f"جلب الصورة من: {url}")
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        img = Image.open(BytesIO(res.content)).convert("RGBA")
        if img.format == 'WEBP':
            png_bytes = BytesIO()
            img.save(png_bytes, format='PNG')
            png_bytes.seek(0)
            img = Image.open(png_bytes).convert("RGBA")
        return img
    except Exception as e:
        print(f"خطأ في جلب الصورة: {e}")
        return None

@app.route('/bnr')
def generate_banner():
    uid = request.args.get("uid")
    region = request.args.get("region", "me")

    if not uid:
        return "يرجى تحديد UID", 400

    try:
        api_url = f"https://razor-info.vercel.app/player-info?uid={uid}&region={region}"
        res = requests.get(api_url, timeout=5).json()
        avatar_id = res.get("basicInfo", {}).get("headPic", 900000013)
    except Exception as e:
        return f"فشل في جلب بيانات اللاعب: {e}", 500

    background = fetch_image(BACKGROUND_IMAGE_URL)
    if not background:
        return "فشل في تحميل الخلفية", 500

    avatar_img = fetch_image(f"https://freefireinfo.vercel.app/icon?id={avatar_id}")
    if avatar_img:
        AVATAR_BOX = (0, 100, 512, 512)
        avatar_width = AVATAR_BOX[2] - AVATAR_BOX[0]
        avatar_height = AVATAR_BOX[3] - AVATAR_BOX[1]
        avatar_img = avatar_img.resize((avatar_width, avatar_height), Image.LANCZOS)
        # استبدال كامل المربع الأحمر بصورة الأفاتار الجديدة
        background.paste(avatar_img, (AVATAR_BOX[0], AVATAR_BOX[1]), avatar_img)

    output = BytesIO()
    background.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')

if __name__ == '__main__':
    app.run()
