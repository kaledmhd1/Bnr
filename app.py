from flask import Flask, request, send_file
from PIL import Image
from io import BytesIO
import requests

app = Flask(__name__)

def fetch_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content)).convert("RGBA")

@app.route("/bnr")
def banner():
    # خلفية من ibb
    background_url = "https://i.ibb.co/LDpHSqVY/IMG-0920.webp"
    background = fetch_image(background_url)

    # الاحتفاظ بالحجم الأصلي للخلفية
    WIDTH, HEIGHT = background.size
    img = Image.new("RGBA", (WIDTH, HEIGHT))
    img.paste(background, (0, 0))

    # جلب صورة الأفاتار
    avatar_id = "900000013"
    avatar_url = f"https://freefireinfo.vercel.app/icon?id={avatar_id}"
    avatar = fetch_image(avatar_url)

    # تغيير حجم الأفاتار ليكون صغيرًا ومتناسبًا مع الخلفية
    avatar_width = 65
    avatar_height = 65
    avatar = avatar.resize((avatar_width, avatar_height))

    # موضع الأفاتار (مكان المربع الأحمر)
    avatar_x = 42  # ← عدّل هذا حسب موقع المربع الأحمر بالضبط
    avatar_y = 43

    img.paste(avatar, (avatar_x, avatar_y), avatar)

    # تصدير الصورة
    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype="image/png")
