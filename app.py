from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

WIDTH, HEIGHT = 1600, 512
BAR_HEIGHT = 100
AVATAR_SIZE = (512, 412)

# مسارات الخطوط
FONT_TEXT_PATH = "ARIAL.TTF"
FONT_SYMBOL_PATH = "DejaVuSans.ttf"
FONT_MIXED_PATH = "NotoSans-Regular.ttf"
FONT_ARABIC_PATH = "NotoSansArabic-Regular.ttf"
FONT_CJK_PATH = "NotoSansCJKjp-Regular.otf"  # خط لدعم CJK (صيني، ياباني، كوري)

# تحميل الخطوط
font_arial = ImageFont.truetype(FONT_TEXT_PATH, 100)
font_dejavu = ImageFont.truetype(FONT_SYMBOL_PATH, 90)
font_noto = ImageFont.truetype(FONT_MIXED_PATH, 130)
font_arabic = ImageFont.truetype(FONT_ARABIC_PATH, 80)
font_cjk = ImageFont.truetype(FONT_CJK_PATH, 100)

def to_halfwidth(text):
    return text.translate({ord(c): ord(c) - 0xFEE0 for c in text if 0xFF01 <= ord(c) <= 0xFF5E})

def contains_arabic(text):
    return any('\u0600' <= c <= '\u06FF' for c in text)

def contains_cjk(text):
    # النطاقات الرئيسية للـ CJK Unified Ideographs
    return any(
        (0x4E00 <= ord(c) <= 0x9FFF) or    # CJK Unified Ideographs
        (0x3400 <= ord(c) <= 0x4DBF) or    # CJK Unified Ideographs Extension A
        (0x3040 <= ord(c) <= 0x309F) or    # Hiragana (ياباني)
        (0x30A0 <= ord(c) <= 0x30FF) or    # Katakana (ياباني)
        (0xAC00 <= ord(c) <= 0xD7AF)       # Hangul Syllables (كوري)
        for c in text
    )

def select_font_for_text(text, size):
    text = to_halfwidth(text)
    if contains_arabic(text):
        return ImageFont.truetype(FONT_ARABIC_PATH, size)
    elif contains_cjk(text):
        return ImageFont.truetype(FONT_CJK_PATH, size)
    else:
        # فقط نص لاتيني أو رموز أخرى، نستخدم NotoSans أو Arial حسب الحجم
        if size > 100:
            return ImageFont.truetype(FONT_MIXED_PATH, size)
        else:
            return ImageFont.truetype(FONT_TEXT_PATH, size)

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
def generate_banner():
    uid = request.args.get("uid")
    region = request.args.get("region", "me")

    if not uid:
        return "يرجى تحديد UID", 400

    try:
        api_url = f"https://razor-info.vercel.app/player-info?uid={uid}&region={region}"
        res = requests.get(api_url, timeout=5).json()

        basic = res.get("basicInfo", {})
        clan = res.get("clanBasicInfo", {})

        nickname_raw = basic.get("nickname", "NoName")
        clan_name_raw = clan.get("clanName", "No Clan")

        nickname = to_halfwidth(nickname_raw)
        clan_name = to_halfwidth(clan_name_raw)

        level = basic.get("level", 1)
        avatar_id = basic.get("headPic", 900000013)
        banner_id = basic.get("bannerId", 900000014)
    except Exception as e:
        return f"❌ فشل في جلب البيانات: {e}", 500

    banner_img_full = fetch_image(f"https://freefireinfo.vercel.app/icon?id={banner_id}")
    banner_img = Image.new("RGBA", (WIDTH, HEIGHT), (25, 25, 25))
    if banner_img_full:
        banner_part = banner_img_full.resize((WIDTH - 512, HEIGHT), Image.LANCZOS)
        banner_img.paste(banner_part, (512, 0))

    img = banner_img.copy()
    draw = ImageDraw.Draw(img)

    # الشريط الأسود العلوي
    draw.rectangle([(0, 0), (WIDTH, BAR_HEIGHT)], fill=(0, 0, 0, 255))

    try:
        bngx_img = Image.open("bngx.jpg.jpeg").convert("RGBA").resize((512, BAR_HEIGHT), Image.LANCZOS)
        img.paste(bngx_img, (0, 0), bngx_img)
    except Exception as e:
        print(f"Error loading bngx image: {e}")

    # كتابة DV:BNGX
    dev_text = to_halfwidth("DV:BNGX")
    font_dev = select_font_for_text(dev_text, 80)
    bbox_dev = font_dev.getbbox(dev_text)
    w_dev = bbox_dev[2] - bbox_dev[0]
    h_dev = bbox_dev[3] - bbox_dev[1]
    text_start_x = 512 + 20
