from flask import Flask, request, send_file
from PIL import Image
from io import BytesIO
import requests

app = Flask(__name__)

@app.route("/bnr")
def generate_banner():
    uid = request.args.get("uid")
    if not uid:
        return "Missing UID", 400

    # تحميل صورة الخلفية الأصلية
    bg_url = "https://i.ibb.co/LDpHSqVY/IMG-0920.webp"
    bg_response = requests.get(bg_url)
    background = Image.open(BytesIO(bg_response.content)).convert("RGBA")

    # تحميل صورة الأفاتار من API
    avatar_url = f"https://freefireinfo.vercel.app/icon?id={uid}"
    avatar_response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(avatar_response.content)).convert("RGBA")

    # تصغير الأفاتار جدًا
    avatar = avatar.resize((80, 65))  # ← الحجم الصغير جدًا المطلوب

    # لصق الأفاتار في أسفل يسار الصورة
    bg_width, bg_height = background.size
    av_width, av_height = avatar.size
    position = (10, bg_height - av_height - 10)  # هامش 10 بكسل من الأسفل واليسار
    background.paste(avatar, position, avatar)

    # تصدير الصورة النهائية
    output = BytesIO()
    background.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype="image/png")
