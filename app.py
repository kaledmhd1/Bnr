from flask import Flask, request, send_file
from PIL import Image
from io import BytesIO
import requests

app = Flask(__name__)

# حجم الصورة النهائية حسب المرجع
WIDTH, HEIGHT = 2048, 512
AVATAR_SIZE = (512, 412)
AVATAR_POSITION = (0, 100)  # مكان الأفاتار حسب الصورة المرجعية

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
    region = request.args.get("region", "me")

    if not uid:
        return "يرجى تحديد UID", 400

    try:
        # جلب بيانات اللاعب
        api_url = f"https://razor-info.vercel.app/player-info?uid={uid}&region={region}"
        res = requests.get(api_url, timeout=5).json()
        avatar_id = res.get("basicInfo", {}).get("headPic", 900000013)
    except Exception as e:
        return f"❌ فشل في جلب البيانات: {e}", 500

    # إنشاء صورة خلفية سوداء فقط
    img = Image.new("RGBA", (WIDTH, HEIGHT), (25, 25, 25))

    # جلب صورة الأفاتار
    avatar_img = fetch_image(f"https://freefireinfo.vercel.app/icon?id={avatar_id}", AVATAR_SIZE)
    if avatar_img:
        img.paste(avatar_img, AVATAR_POSITION, avatar_img)

    # إخراج الصورة
    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')

if __name__ == '__main__':
    app.run()
