from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

app = Flask(__name__)

WIDTH, HEIGHT = 2048, 512
FONT_PATH = "ARIAL.TTF"

font_nickname = ImageFont.truetype(FONT_PATH, 150)
font_large = ImageFont.truetype(FONT_PATH, 90)
font_level = ImageFont.truetype(FONT_PATH, 100)

def fetch_image(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
        return Image.open(BytesIO(res.content)).convert("RGBA")
    except:
        return None

def get_url(icon_id):
    return f"https://freefireinfo.vercel.app/icon?id={icon_id}"

def resize_and_crop(img, target_size):
    img_ratio = img.width / img.height
    target_ratio = target_size[0] / target_size[1]

    # نغير الحجم ليغطي كامل الخلفية بدون تشويه
    if img_ratio > target_ratio:
        new_height = target_size[1]
        new_width = int(new_height * img_ratio)
    else:
        new_width = target_size[0]
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    # ثم نقصها لتناسب الحجم المطلوب تمامًا
    left = (img.width - target_size[0]) // 2
    top = (img.height - target_size[1]) // 2
    right = left + target_size[0]
    bottom = top + target_size[1]

    return img.crop((left, top, right, bottom))

@app.route("/bnr")
def banner_image():
    uid = request.args.get("uid")
    if not uid:
        return jsonify({"error": "Thiếu uid"}), 400

    region = "me"

    try:
        api = f"https://razor-info.vercel.app/player-info?uid={uid}&region={region}"
        res = requests.get(api).json()
    except:
        return jsonify({"error": "Không thể lấy dữ liệu từ API"}), 500

    basic = res.get("basicInfo", {})
    clan = res.get("clanBasicInfo", {})

    nickname = basic.get("nickname", "NoName")
    level = basic.get("level", 1)
    avatar_id = basic.get("headPic", 900000013)
    banner_id = basic.get("bannerId", 900000014)
    pin_id = basic.get("pinId")
    guild = clan.get("clanName", "No Guild")

    bg_raw = fetch_image(get_url(banner_id))
    avatar = fetch_image(get_url(avatar_id)).resize((512, 512), Image.LANCZOS)
    pin = fetch_image(get_url(pin_id)).resize((128, 128), Image.LANCZOS) if pin_id else None

    if not bg_raw or not avatar:
        return jsonify({"error": "Không tải được ảnh"}), 500

    # ملء الخلفية مع الاقتصاص لتكون 2048x512 دون تشويه
    bg = resize_and_crop(bg_raw, (WIDTH, HEIGHT))

    final_img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    final_img.paste(bg, (0, 0))

    final_img.paste(avatar, (0, 0), avatar)
    if pin:
        final_img.paste(pin, (30, 384), pin)

    draw = ImageDraw.Draw(final_img)

    bar_height = 100
    bar_y = HEIGHT - bar_height
    avatar_width = 512

    draw.rectangle(
        [(avatar_width, bar_y), (WIDTH, HEIGHT)],
        fill=(100, 100, 100, 230)
    )

    dev_text = "DEV:BNGX"
    text_bbox = font_large.getbbox(dev_text)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = avatar_width + (WIDTH - avatar_width - text_width) // 15
    text_y = bar_y - 27
    draw.text((text_x, text_y), dev_text, font=font_large, fill="white")

    draw.text((550, 20), nickname, font=font_nickname, fill="white")
    draw.text((550, 250), guild, font=font_large, fill="white")
    draw.text((WIDTH - 320, HEIGHT - 230), f"Lvl. {level}", font=font_level, fill="white")

    buf = BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
