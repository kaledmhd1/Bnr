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

    # حجم الصورة النهائية
    WIDTH, HEIGHT = 2048, 512

    # خلفية شفافة بالحجم المطلوب
    final_image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))

    # تحميل الخلفية
    bg_url = "https://i.ibb.co/LDpHSqVY/IMG-0920.webp"
    bg_response = requests.get(bg_url)
    if bg_response.status_code != 200:
        return "Failed to load background image", 500

    background = Image.open(BytesIO(bg_response.content)).convert("RGBA")

    # الحفاظ على النسبة: تصغير لتناسب الصورة النهائية (fit)
    bg_ratio = min(WIDTH / background.width, HEIGHT / background.height)
    new_bg_size = (int(background.width * bg_ratio), int(background.height * bg_ratio))
    background = background.resize(new_bg_size, Image.LANCZOS)

    # حساب موضع لصق الخلفية لتكون في المنتصف
    bg_x = (WIDTH - background.width) // 2
    bg_y = (HEIGHT - background.height) // 2
    final_image.paste(background, (bg_x, bg_y), background)

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
    avatar = avatar.resize((150, 120))

    # لصق الأفاتار في أسفل يسار الصورة
    av_width, av_height = avatar.size
    av_x = 20
    av_y = HEIGHT - av_height - 20
    final_image.paste(avatar, (av_x, av_y), avatar)

    # تصدير الصورة
    output = BytesIO()
    final_image.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype="image/png")
