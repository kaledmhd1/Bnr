from flask import Flask, request, send_file
from PIL import Image
from io import BytesIO
import requests

app = Flask(__name__)

# أبعاد الصورة
WIDTH, HEIGHT = 2048, 512
AVATAR_SIZE = (512, 412)
AVATAR_POSITION = (0, 100)  # الموضع فوق الخلفية

# رابط الخلفية (من imgur بصيغة مباشرة)
BACKGROUND_IMAGE_URL = "https://i.imgur.com/o5KH4I9.png"

def fetch_image(url, size=None):
    try:
        print(f"📥 جلب الصورة من: {url}")
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        img = Image.open(BytesIO(res.content)).convert("RGBA")
        if size:
            img = img.resize(size, Image.LANCZOS)
        return img
    except Exception as e:
        print(f"❌ خطأ في جلب الصورة: {e}")
        return None

@app.route('/bnr')
def generate_avatar_on_custom_background():
    uid = request.args.get("uid")
    region = request.args.get("region", "me")

    if not uid:
        return "يرجى تحديد UID", 400

    try:
        # جلب بيانات اللاعب من API
        api_url = f"https://razor-info.vercel.app/player-info?uid={uid}&region={region}"
        res = requests.get(api_url, timeout=5).json()
        avatar_id = res.get("basicInfo", {}).get("headPic", 900000013)
    except Exception as e:
        return f"❌ فشل في جلب بيانات اللاعب: {e}", 500

    # جلب الخلفية
    background = fetch_image(BACKGROUND_IMAGE_URL, (WIDTH, HEIGHT))
    if not background:
        return "❌ فشل في تحميل الخلفية", 500

    # جلب الأفاتار
    avatar_img = fetch_image(f"https://freefireinfo.vercel.app/icon?id={avatar_id}", AVATAR_SIZE)
    if avatar_img:
        background.paste(avatar_img, AVATAR_POSITION, avatar_img)
    else:
        print("⚠️ لم يتم جلب صورة الأفاتار.")

    # إخراج الصورة النهائية
    output = BytesIO()
    background.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')

if __name__ == '__main__':
    app.run()
