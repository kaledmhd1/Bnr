from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

WIDTH, HEIGHT = 2048, 512
FONT_TEXT_PATH = "ARIAL.TTF"
FONT_SYMBOL_PATH = "DejaVuSans.ttf"
FONT_MIXED_PATH = "NotoSans-Regular.ttf"

font_nickname = ImageFont.truetype(FONT_MIXED_PATH, 130)
font_level = ImageFont.truetype(FONT_SYMBOL_PATH, 90)
font_clan = ImageFont.truetype(FONT_TEXT_PATH, 100)
font_dev = ImageFont.truetype(FONT_MIXED_PATH, 45)

@app.route('/bnr')
def generate_banner():
    uid = request.args.get("uid")
    region = request.args.get("region", "me")
    
    if not uid:
        return "UID مطلوب", 400
    
    # جلب معلومات اللاعب
    try:
        info = requests.get(f"https://freefireinfo.vercel.app/info?uid={uid}&region={region}").json()
        nickname = info["nickname"]
        level = info["level"]
        clan = info.get("clan", {}).get("name", "")
    except Exception as e:
        return f"❌ فشل في جلب البيانات: {e}", 500

    # إنشاء الصورة
    img = Image.new("RGBA", (WIDTH, HEIGHT), (25, 25, 25))
    draw = ImageDraw.Draw(img)

    # شريط رمادي
    draw.rectangle([(500, 0), (WIDTH, HEIGHT)], fill=(40, 40, 40))

    # تحميل صورة الأيقونة
    try:
        icon_url = f"https://freefireinfo.vercel.app/icon?id={uid}"
        icon = Image.open(BytesIO(requests.get(icon_url).content)).convert("RGBA").resize((512, 512))
        img.paste(icon, (0, 0))
    except Exception:
        pass

    # الكتابة على الصورة
    draw.text((550, 90), nickname, font=font_nickname, fill="white")
    draw.text((550, 260), f"Lv. {level}", font=font_level, fill="white")
    draw.text((550, 360), clan, font=font_clan, fill="white")
    draw.text((1900, 10), "DV:B𝙽𝙂𝚇", font=font_dev, fill="white")

    # إخراج الصورة
    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')

if __name__ == '__main__':
    app.run()
