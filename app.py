from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

# مقاسات الصورة النهائية ستكون نفس الخلفية
def fetch_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content)).convert("RGBA")

@app.route("/bnr")
def banner():
    uid = request.args.get("uid")
    region = request.args.get("region")

    # جلب الخلفية
    bg_url = "https://i.ibb.co/LDpHSqVY/IMG-0920.webp"
    background = fetch_image(bg_url)
    WIDTH, HEIGHT = background.size  # نحافظ على الحجم الأصلي

    # إنشاء صورة جديدة بنفس حجم الخلفية
    img = Image.new("RGBA", (WIDTH, HEIGHT))
    img.paste(background, (0, 0))

    # جلب الأفاتار وتصغيره جدًا
    avatar_id = "900000013"
    avatar_url = f"https://freefireinfo.vercel.app/icon?id={avatar_id}"
    avatar = fetch_image(avatar_url)
    avatar = avatar.resize((60, 48))  # تصغير قوي

    # وضع الأفاتار مكان المربع الأحمر (أعلى اليسار مثلًا)
    avatar_x = 20
    avatar_y = 20
    img.paste(avatar, (avatar_x, avatar_y), avatar)

    # إرسال الصورة
    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype="image/png")
