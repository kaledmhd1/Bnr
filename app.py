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

    # تحميل الخلفية من الرابط
    bg_url = "https://i.ibb.co/LDpHSqVY/IMG-0920.webp"
    bg_response = requests.get(bg_url)
    if bg_response.status_code != 200:
        return "Failed to load background image", 500

    background = Image.open(BytesIO(bg_response.content)).convert("RGBA")

    # حجم الصورة النهائية
    WIDTH, HEIGHT = 2048, 512
    background = background.resize((WIDTH, HEIGHT))  # ✅ نغير حجم الخلفية لتناسب الأبعاد

    # تحميل صورة الأفاتار
    avatar_url = f"https://freefireinfo.vercel.app/icon?id={uid}"
    avatar_response = requests.get(avatar_url)
    if avatar_response.status_code != 200 or 'image' not in avatar_response.headers.get('Content-Type', ''):
        return f"Failed to load avatar for UID {uid}", 400

    try:
        avatar = Image.open(BytesIO(avatar_response.content)).convert("RGBA")
    except Exception as e:
        return f"Error loading avatar image: {e}", 500

    # تصغير الأفاتار لحجم مناسب
    avatar = avatar.resize((150, 120))  # ✅ حجم مناسب

    # لصق الأفاتار في أسفل يسار الصورة
    av_width, av_height = avatar.size
    position = (20, HEIGHT - av_height - 20)
    background.paste(avatar, position, avatar)

    # تصدير الصورة
    output = BytesIO()
    background.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype="image/png")
