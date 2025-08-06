from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

# إعدادات الصورة
WIDTH, HEIGHT = 2048, 512
BAR_HEIGHT = 100

# الخطوط
FONT_MIXED_PATH = "NotoSansArabic-Regular.ttf"  # يدعم العربية واللاتينية والزخارف

# إعدادات الخطوط
font_nickname = ImageFont.truetype(FONT_MIXED_PATH, 130)
font_level = ImageFont.truetype(FONT_MIXED_PATH, 90)
font_clan = ImageFont.truetype(FONT_MIXED_PATH, 100)
font_dev = ImageFont.truetype(FONT_MIXED_PATH, 80)

@app.route("/bnr")
def generate_banner():
    uid = request.args.get("uid")
    region = request.args.get("region", "me")

    if not uid:
        return "يرجى تحديد UID", 400

    # جلب بيانات اللاعب من API خارجي
    info_url = f"https://info-ch9ayfa.vercel.app/{uid}?region={region}"
    try:
        response = requests.get(info_url)
        data = response.json()
    except Exception as e:
        return f"فشل في جلب البيانات: {e}", 500

    nickname = data.get("nickname", "Unknown")
    level = data.get("level", "??")
    clan = data.get("clan", "")
    avatar_url = data.get("avatar")

    # إنشاء صورة جديدة
    banner = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))

    # جلب صورة البنر
    banner_url = data.get("banner")
    if banner_url:
        try:
            banner_img = Image.open(BytesIO(requests.get(banner_url).content)).convert("RGB")
            banner_img = banner_img.resize((WIDTH, HEIGHT))
            banner.paste(banner_img, (0, 0))
        except:
            pass  # تجاهل إذا فشل تحميل البنر

    # رسم الشريط الأسود العلوي
    draw = ImageDraw.Draw(banner)
    draw.rectangle((0, 0, WIDTH, BAR_HEIGHT), fill="black")

    # جلب صورة الأفاتار
    if avatar_url:
        try:
            avatar_img = Image.open(BytesIO(requests.get(avatar_url).content)).convert("RGB")
            avatar_img = avatar_img.resize((350, 350))
            banner.paste(avatar_img, (80, 80))
        except:
            pass

    # كتابة الاسم
    draw.text((480, 120), nickname, font=font_nickname, fill="white")

    # كتابة LV.XX
    draw.text((480, 250), f"Lv. {level}", font=font_level, fill="white")

    # اسم الكلان إذا موجود
    if clan:
        draw.text((WIDTH - 900, 120), clan, font=font_clan, fill="white")

    # الكتابة DV:BNGX على الشريط الأسود
    dev_text = "DV:BNGX"
    w_dev, h_dev = draw.textsize(dev_text, font=font_dev)
    draw.text((WIDTH - w_dev - 40, (BAR_HEIGHT - h_dev) // 2), dev_text, font=font_dev, fill="white")

    # تحويل الصورة إلى استجابة Flask
    img_io = BytesIO()
    banner.save(img_io, "PNG")
    img_io.seek(0)
    return send_file(img_io, mimetype="image/png")

if __name__ == "__main__":
    app.run()
