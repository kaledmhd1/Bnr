from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

AVATAR_SIZE = (125, 125)
FONT_PRIMARY = "Tajawal-Bold.ttf"
FONT_FALLBACKS = [
    "DejaVuSans.ttf",
    "NotoSans-Regular.ttf",
    "ARIAL.TTF",
    "NotoSansArabic-Regular.ttf",
    "NotoSansSymbols2-Regular.ttf",
    "NotoSansCJKjp-Regular.otf",
    "unifont-15.0.01.ttf"
]
SECRET_KEY = "BNGX"

# تحميل الخطوط مسبقًا
def load_fonts(sizes):
    fonts = {"primary": {}, "fallbacks": []}
    for size in sizes:
        try:
            fonts["primary"][size] = ImageFont.truetype(FONT_PRIMARY, size)
        except:
            fonts["primary"][size] = ImageFont.load_default()
    for font_path in FONT_FALLBACKS:
        fallback_fonts = {}
        for size in sizes:
            try:
                fallback_fonts[size] = ImageFont.truetype(font_path, size)
            except:
                fallback_fonts[size] = None
        fonts["fallbacks"].append(fallback_fonts)
    return fonts

fonts = load_fonts([30, 35, 40, 50])

def char_in_font(char, font):
    try:
        glyph = font.getmask(char)
        return glyph.getbbox() is not None
    except:
        return False

def smart_draw_text(draw, position, text, font_dict, size, fill):
    x, y = position
    primary_font = font_dict["primary"][size]
    fallbacks = font_dict["fallbacks"]

    for char in text:
        font_to_use = None
        if char_in_font(char, primary_font):
            font_to_use = primary_font
        else:
            for fb_fonts in fallbacks:
                fb_font = fb_fonts[size]
                if fb_font and char_in_font(char, fb_font):
                    font_to_use = fb_font
                    break
        if not font_to_use:
            font_to_use = primary_font

        draw.text((x, y), char, font=font_to_use, fill=fill)
        char_width = font_to_use.getbbox(char)[2] - font_to_use.getbbox(char)[0]
        x += char_width

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
    key = request.args.get("key")

    if key != SECRET_KEY:
        return "🚫 مفتاح غير صحيح", 403

    if not uid:
        return "يرجى تحديد UID", 400

    # جلب معلومات اللاعب من الرابط الجديد
    try:
        api_url = f"https://infor-bngx-ff.vercel.app/get?uid={uid}"
        res = requests.get(api_url, timeout=5)
        res.raise_for_status()
        data = res.json()
        account_info = data.get("AccountInfo", {})
        nickname = account_info.get("AccountName", "Unknown")
        likes = account_info.get("AccountLikes", 0)
        level = account_info.get("AccountLevel", 0)
        avatar_id = account_info.get("AccountAvatarId")
    except Exception as e:
        return f"❌ فشل في جلب البيانات: {e}", 500

    bg_img = fetch_image("https://i.postimg.cc/L4PQBgmx/IMG-20250807-042134-670.jpg")
    if not bg_img:
        return "❌ فشل في تحميل الخلفية", 500

    img = bg_img.copy()
    draw = ImageDraw.Draw(img)

    avatar_img = fetch_image(f"https://freefireinfo.vercel.app/icon?id={avatar_id}", AVATAR_SIZE)
    avatar_x, avatar_y = 90, 82
    if avatar_img:
        img.paste(avatar_img, (avatar_x, avatar_y), avatar_img)

    level_text = f"Lv. {level}"
    level_x = avatar_x - 40
    level_y = avatar_y + 160
    smart_draw_text(draw, (level_x, level_y), level_text, fonts, 50, "black")

    nickname_x = avatar_x + AVATAR_SIZE[0] + 80
    nickname_y = avatar_y - 3
    smart_draw_text(draw, (nickname_x, nickname_y), nickname, fonts, 50, "black")

    bbox_uid = fonts["primary"][35].getbbox(uid)
    text_w = bbox_uid[2] - bbox_uid[0]
    text_h = bbox_uid[3] - bbox_uid[1]
    img_w, img_h = img.size
    text_x = img_w - text_w - 110
    text_y = img_h - text_h - 17
    smart_draw_text(draw, (text_x, text_y), uid, fonts, 35, "white")

    likes_text = f"{likes}"
    bbox_likes = fonts["primary"][40].getbbox(likes_text)
    likes_w = bbox_likes[2] - bbox_likes[0]
    likes_y = text_y - (bbox_likes[3] - bbox_likes[1]) - 25
    likes_x = img_w - likes_w - 60
    smart_draw_text(draw, (likes_x, likes_y), likes_text, fonts, 40, "black")

    dev_text = "DEV BY : BNGX"
    bbox_dev = fonts["primary"][30].getbbox(dev_text)
    dev_w = bbox_dev[2] - bbox_dev[0]
    padding = 30
    dev_x = img_w - dev_w - padding
    dev_y = padding
    smart_draw_text(draw, (dev_x, dev_y), dev_text, fonts, 30, "white")

    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')

