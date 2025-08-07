from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

def fetch_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content)).convert("RGBA")

@app.route("/bnr")
def banner():
    uid = request.args.get("uid")
    region = request.args.get("region")

    # جلب الخلفية بالحجم الأصلي
    bg_url = "https://i.ibb.co/LDpHSqVY/IMG-0920.webp"
    background = fetch_image(bg_url)
    WIDTH, HEIGHT = background.size

    # إنشاء صورة بنفس حجم الخلفية
    img = Image.new("RGBA", (WIDTH, HEIGHT))
    img.paste(background, (0, 0))

    # جلب الأفاتار
    avatar_id = "900000013"
    avatar_url = f"https://freefireinfo.vercel.app/icon?id={avatar_id}"
    avatar = fetch_image(avatar_url)

    # تصغير الأفاتار بشكل ملائم (مثال: 50x40 أو أصغر حسب التجربة)
    avatar_width = 50
    avatar_height = 40
    avatar = avatar.resize((avatar_width, avatar_height))

    # تحديد الموضع المناسب داخل الخلفية (مكان المربع الأحمر)
    avatar_x = 30  # تحكم أفقيًا
    avatar_y = 20  # تحكم رأسيًا

    # لصق الأفاتار داخل الخلفية
    img.paste(avatar, (avatar_x, avatar_y), avatar)

    # تصدير الصورة
    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype="image/png")
