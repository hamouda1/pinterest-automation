import sys
import io
import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

W, H = 1000, 1500

from pathlib import Path
FONTS_DIR_CANDIDATE = Path(__file__).resolve().parent / "fonts"
FONT_DIR = str(FONTS_DIR_CANDIDATE) if FONTS_DIR_CANDIDATE.exists() else r"C:\Windows\Fonts"

# High-End 2026 Typography
FONT_TITLE_SERIF = ImageFont.truetype(os.path.join(FONT_DIR, "georgiab.ttf"), 48)
FONT_TITLE_MED = ImageFont.truetype(os.path.join(FONT_DIR, "georgiab.ttf"), 40)
FONT_SUB_ITALIC = ImageFont.truetype(os.path.join(FONT_DIR, "georgiai.ttf"), 26)
FONT_HEADER_CAPS = ImageFont.truetype(os.path.join(FONT_DIR, "corbelb.ttf"), 24)
FONT_BODY_CLEAN = ImageFont.truetype(os.path.join(FONT_DIR, "corbel.ttf"), 22)
FONT_BADGE = ImageFont.truetype(os.path.join(FONT_DIR, "corbelb.ttf"), 19)

STUDIO_BACKGROUNDS = [
    (246, 243, 238),  # Warm Linen
    (243, 240, 234),  # Nordic Travertine
    (239, 236, 230),  # Soft Oatmeal
    (245, 241, 236),  # Sandstone Pearl
    (241, 238, 233),  # French Alabaster
]

SPLIT_ACCENT_COLORS = [
    (48, 42, 38),     # Espresso Noir
    (62, 54, 46),     # Warm Walnut
    (55, 62, 56),     # Forest Sage
    (74, 52, 45),     # Deep Terracotta
    (42, 48, 56),     # Nordic Slate
]

def is_image_white_cutout(img):
    """
    Analyzes an image's corners and pixels to detect if it's an isolated white cutout.
    """
    rgb = img.convert("RGB")
    iw, ih = rgb.size
    
    corners = [
        rgb.getpixel((10, 10)),
        rgb.getpixel((iw - 10, 10)),
        rgb.getpixel((10, ih - 10)),
        rgb.getpixel((iw - 10, ih - 10))
    ]
    corners_white = all(r > 240 and g > 240 and b > 240 for r, g, b in corners)
    
    small = rgb.resize((50, 50))
    pixels = list(small.getdata())
    white_count = sum(1 for r, g, b in pixels if r > 240 and g > 240 and b > 240)
    white_ratio = white_count / len(pixels)
    
    return corners_white and (white_ratio > 0.28)

def clean_title_words(title, max_len=60):
    clean = title.split("|")[0].split(" - ")[0].strip()
    if len(clean) > max_len:
        clean = clean[:max_len - 3] + "..."
    return clean

# -------------------------------------------------------------
# TEMPLATE 1: Editorial Lifestyle (Full Bleed Magazine)
# -------------------------------------------------------------
def render_editorial_lifestyle(prod_img, title, board_id, queue_index=1):
    raw = prod_img.convert("RGBA")
    rw, rh = raw.size
    
    target_ratio = W / H
    current_ratio = rw / rh
    if current_ratio > target_ratio:
        new_w = int(rh * target_ratio)
        left = (rw - new_w) // 2
        crop_box = (left, 0, left + new_w, rh)
    else:
        new_h = int(rw / target_ratio)
        top = int((rh - new_h) * 0.22)
        crop_box = (0, top, rw, top + new_h)
        
    cropped = raw.crop(crop_box).resize((W, H), Image.LANCZOS)
    
    gradient = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(gradient)
    
    for y in range(0, 160):
        alpha = int(130 * (1 - y / 160))
        gdraw.line([(0, y), (W, y)], fill=(15, 15, 15, alpha))
        
    for y in range(920, H):
        progress = (y - 920) / (H - 920)
        alpha = int(225 * (progress ** 1.4))
        gdraw.line([(0, y), (W, y)], fill=(12, 12, 14, alpha))
        
    pin = Image.alpha_composite(cropped, gradient)
    draw = ImageDraw.Draw(pin)
    
    b_id = str(board_id)
    if any(k in b_id for k in ["945", "946", "947", "948", "949", "950"]):
        header_text = "R I T U A L I S T I C   H O M E   •   F R A G R A N C E"
        badge_text = "SCENT STACKING RITUAL"
    elif any(k in b_id for k in ["326", "327", "328", "329", "330", "331", "208", "259"]):
        header_text = "C O Z Y   H O M E   •   A E S T H E T I C   S T Y L E"
        badge_text = "CURATED HOME ESSENTIAL"
    elif any(k in b_id for k in ["518", "519", "520", "521", "522", "523"]):
        header_text = "M I N I M A L I S T   D E S K   •   W O R K S P A C E"
        badge_text = "AESTHETIC WFH FIND"
    else:
        header_text = "A E S T H E T I C   S T R E E T W E A R   •   L O O K B O O K"
        badge_text = "TRENDING 2026 OUTFIT"
        
    bbox = FONT_HEADER_CAPS.getbbox(header_text)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 55), header_text, font=FONT_HEADER_CAPS, fill=(245, 245, 240, 235))
    
    px = 65
    py = 1050
    pbbox = FONT_BADGE.getbbox(badge_text)
    pw = pbbox[2] - pbbox[0] + 34
    draw.rounded_rectangle([px, py, px + pw, py + 36], radius=5, fill=(255, 255, 255, 35), outline=(255, 255, 255, 75), width=1)
    draw.text((px + 17, py + 7), badge_text, font=FONT_BADGE, fill=(255, 255, 255, 240))
    
    clean_title = clean_title_words(title, 60)
    words = clean_title.split()
    line1, line2 = "", ""
    for w in words:
        if len(f"{line1} {w}".strip()) <= 26:
            line1 = f"{line1} {w}".strip()
        else:
            line2 = f"{line2} {w}".strip()
            
    draw.text((px, 1115), line1, font=FONT_TITLE_SERIF, fill=(255, 255, 255))
    if line2:
        draw.text((px, 1175), line2[:32], font=FONT_TITLE_SERIF, fill=(255, 255, 255))
        y_sub = 1255
    else:
        y_sub = 1195
        
    draw.text((px, y_sub), "Curated Amazon Favorite  •  Verified High Ratings  •  Exclusive Design", font=FONT_BODY_CLEAN, fill=(230, 225, 220, 230))
    draw.line([(px, y_sub + 45), (W - px, y_sub + 45)], fill=(255, 255, 255, 60), width=1)
    
    draw.text((px, y_sub + 75), "TAP TO SHOP THIS LOOK ON AMAZON ↗", font=FONT_HEADER_CAPS, fill=(255, 255, 255))
    draw.text((W - 120, y_sub + 77), "#ad", font=FONT_BODY_CLEAN, fill=(200, 200, 200))
    
    return pin.convert("RGB")

# -------------------------------------------------------------
# TEMPLATE 2: Studio Flat Lay (3D Shadow on Organic Linen)
# -------------------------------------------------------------
def render_studio_flatlay(prod_img, title, board_id, queue_index=1):
    bg_color = STUDIO_BACKGROUNDS[queue_index % len(STUDIO_BACKGROUNDS)]
    pin = Image.new("RGBA", (W, H), (*bg_color, 255))
    draw = ImageDraw.Draw(pin)
    
    draw.rectangle([30, 30, W - 30, H - 30], outline=(225, 220, 212), width=1)
    
    target_w = 780
    scale = min(target_w / prod_img.width, 820 / prod_img.height)
    new_pw = int(prod_img.width * scale)
    new_ph = int(prod_img.height * scale)
    raw = prod_img.convert("RGBA").resize((new_pw, new_ph), Image.LANCZOS)
    
    datas = raw.getdata()
    new_data = []
    for item in datas:
        r, g, b = item[0], item[1], item[2]
        if r > 245 and g > 245 and b > 245:
            new_data.append((255, 255, 255, 0))
        elif r > 230 and g > 230 and b > 230:
            diff = (r + g + b) / 3 - 230
            alpha = max(0, min(255, int(255 * (1 - diff / 15))))
            new_data.append((r, g, b, alpha))
        else:
            new_data.append((r, g, b, 255))
    raw.putdata(new_data)
    prod_resized = raw
    
    prod_x = (W - new_pw) // 2
    prod_y = 190 + (800 - new_ph) // 2
    
    shadow_w = new_pw + 80
    shadow_h = 130
    shadow = Image.new("RGBA", (shadow_w, shadow_h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse([40, 25, shadow_w - 40, shadow_h - 20], fill=(65, 55, 45, 65))
    shadow = shadow.filter(ImageFilter.GaussianBlur(32))
    
    c_shadow = Image.new("RGBA", (shadow_w, shadow_h), (0, 0, 0, 0))
    csdraw = ImageDraw.Draw(c_shadow)
    csdraw.ellipse([90, 40, shadow_w - 90, shadow_h - 30], fill=(35, 30, 25, 115))
    c_shadow = c_shadow.filter(ImageFilter.GaussianBlur(14))
    
    shadow_y = prod_y + new_ph - 70
    pin.paste(shadow, ((W - shadow_w) // 2, shadow_y), shadow)
    pin.paste(c_shadow, ((W - shadow_w) // 2, shadow_y + 8), c_shadow)
    pin.paste(prod_resized, (prod_x, prod_y), prod_resized)
    
    draw = ImageDraw.Draw(pin)
    num_str = f"NO. {(queue_index % 60) + 1:02d}"
    draw.text((65, 65), f"{num_str}  /  CURATED ESSENTIALS", font=FONT_HEADER_CAPS, fill=(135, 125, 115))
    draw.text((W - 200, 65), "AMAZON FIND", font=FONT_HEADER_CAPS, fill=(180, 130, 70))
    draw.line([(65, 105), (W - 65, 105)], fill=(225, 220, 212), width=1)
    
    y_text = 1090
    clean_title = clean_title_words(title, 60)
    words = clean_title.split()
    line1, line2 = "", ""
    for w in words:
        if len(f"{line1} {w}".strip()) <= 28:
            line1 = f"{line1} {w}".strip()
        else:
            line2 = f"{line2} {w}".strip()
            
    draw.text((65, y_text), line1, font=FONT_TITLE_MED, fill=(35, 32, 28))
    if line2:
        draw.text((65, y_text + 55), line2[:34], font=FONT_TITLE_MED, fill=(35, 32, 28))
        y_spec = y_text + 120
    else:
        y_spec = y_text + 65
        
    specs = "Premium Quality Craftsmanship  •  Verified High Ratings  •  Trending Design"
    draw.text((65, y_spec), specs, font=FONT_BODY_CLEAN, fill=(120, 110, 100))
    draw.line([(65, y_spec + 45), (W - 65, y_spec + 45)], fill=(225, 220, 212), width=1)
    
    draw.text((65, y_spec + 75), "TAP TO CHECK CURRENT PRICE & SIZING ↗", font=FONT_HEADER_CAPS, fill=(35, 32, 28))
    draw.text((W - 120, y_spec + 77), "#ad", font=FONT_BODY_CLEAN, fill=(160, 150, 140))
    
    return pin.convert("RGB")

# -------------------------------------------------------------
# TEMPLATE 3: Minimalist Polaroid / Elevated Gallery Frame
# -------------------------------------------------------------
def render_polaroid_gallery(prod_img, title, board_id, queue_index=1):
    base = Image.new("RGBA", (W, H), (248, 246, 242, 255))
    draw = ImageDraw.Draw(base)
    draw.rectangle([25, 25, W - 25, H - 25], outline=(225, 220, 212), width=1)

    draw.text((65, 60), f"NO. {(queue_index % 60) + 1:02d}  /  GALLERY SELECTION", font=FONT_HEADER_CAPS, fill=(140, 130, 120))
    draw.text((W - 190, 60), "CURATED 2026", font=FONT_HEADER_CAPS, fill=(180, 130, 70))
    draw.line([(65, 98), (W - 65, 98)], fill=(225, 220, 212), width=1)

    pw, ph = 860, 1080
    px, py = 70, 140
    
    shadow = Image.new("RGBA", (pw + 60, ph + 60), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle([20, 20, pw + 40, ph + 40], radius=12, fill=(40, 35, 30, 38))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    base.paste(shadow, (px - 20, py - 10), shadow)

    card = Image.new("RGBA", (pw, ph), (255, 255, 255, 255))
    cdraw = ImageDraw.Draw(card)
    cdraw.rounded_rectangle([0, 0, pw, ph], radius=8, outline=(235, 230, 222), width=1)

    photo_w, photo_h = pw - 60, 780
    raw = prod_img.convert("RGBA")
    scale = min(photo_w / raw.width, photo_h / raw.height)
    new_w, new_h = int(raw.width * scale), int(raw.height * scale)
    photo_resized = raw.resize((new_w, new_h), Image.LANCZOS)
    
    card.paste(photo_resized, (30 + (photo_w - new_w) // 2, 30 + (photo_h - new_h) // 2), photo_resized)

    clean_title = clean_title_words(title, 42)
    cdraw.text((40, 840), clean_title, font=FONT_TITLE_MED, fill=(35, 32, 28))
    cdraw.text((40, 905), "Aesthetic Wardrobe & Decor Essential  •  Verified High Ratings", font=FONT_SUB_ITALIC, fill=(120, 110, 100))
    cdraw.line([(40, 955), (pw - 40, 955)], fill=(235, 230, 222), width=1)
    
    cdraw.text((40, 985), "SHOP NOW ON AMAZON ↗", font=FONT_HEADER_CAPS, fill=(35, 32, 28))
    cdraw.text((pw - 90, 987), "#ad", font=FONT_BODY_CLEAN, fill=(160, 150, 140))

    base.paste(card, (px, py), card)
    
    bdraw = ImageDraw.Draw(base)
    bdraw.text((65, 1270), "TAP PIN TO VIEW PRODUCT SPECS, REVIEWS & PRICING", font=FONT_HEADER_CAPS, fill=(100, 92, 85))
    bdraw.text((65, 1315), "Handpicked for effortless quality, timeless design & everyday elegance.", font=FONT_BODY_CLEAN, fill=(130, 120, 110))

    return base.convert("RGB")

# -------------------------------------------------------------
# TEMPLATE 4: Dark Luxury / Modern Slate (Gold Glow & Contrast)
# -------------------------------------------------------------
def render_dark_luxury(prod_img, title, board_id, queue_index=1):
    base = Image.new("RGBA", (W, H), (20, 20, 24, 255))
    draw = ImageDraw.Draw(base)
    
    draw.rectangle([30, 30, W - 30, H - 30], outline=(75, 65, 50), width=1)

    glow = Image.new("RGBA", (700, 700), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([50, 50, 650, 650], fill=(95, 75, 45, 80))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    base.paste(glow, ((W - 700) // 2, 180), glow)

    raw = prod_img.convert("RGBA")
    scale = min(760 / raw.width, 760 / raw.height)
    new_w, new_h = int(raw.width * scale), int(raw.height * scale)
    prod_resized = raw.resize((new_w, new_h), Image.LANCZOS)
    
    c_shadow = Image.new("RGBA", (new_w + 40, 80), (0, 0, 0, 0))
    csdraw = ImageDraw.Draw(c_shadow)
    csdraw.ellipse([20, 10, new_w + 20, 70], fill=(0, 0, 0, 160))
    c_shadow = c_shadow.filter(ImageFilter.GaussianBlur(18))
    
    py = 220 + (740 - new_h) // 2
    base.paste(c_shadow, ((W - new_w - 40) // 2, py + new_h - 40), c_shadow)
    base.paste(prod_resized, ((W - new_w) // 2, py), prod_resized)

    draw.text((65, 65), "THE EDITORIAL LUXURY COLLECTION", font=FONT_HEADER_CAPS, fill=(210, 180, 130))
    draw.text((W - 190, 65), "AMAZON FIND", font=FONT_HEADER_CAPS, fill=(160, 140, 110))
    draw.line([(65, 105), (W - 65, 105)], fill=(75, 65, 50), width=1)

    clean_title = clean_title_words(title, 60)
    words = clean_title.split()
    line1, line2 = "", ""
    for w in words:
        if len(f"{line1} {w}".strip()) <= 26:
            line1 = f"{line1} {w}".strip()
        else:
            line2 = f"{line2} {w}".strip()

    draw.text((65, 1070), line1, font=FONT_TITLE_SERIF, fill=(255, 255, 255))
    if line2:
        draw.text((65, 1130), line2[:32], font=FONT_TITLE_SERIF, fill=(255, 255, 255))
        y_spec = 1210
    else:
        y_spec = 1150
        
    draw.text((65, y_spec), "Curated High-End Aesthetic  •  Top Verified Ratings  •  Exclusive Style", font=FONT_BODY_CLEAN, fill=(180, 175, 165))
    draw.line([(65, y_spec + 45), (W - 65, y_spec + 45)], fill=(75, 65, 50), width=1)
    
    btn_w, btn_h = 420, 50
    draw.rounded_rectangle([65, y_spec + 75, 65 + btn_w, y_spec + 75 + btn_h], radius=6, fill=(210, 180, 130, 240))
    draw.text((95, y_spec + 88), "DISCOVER ON AMAZON ↗", font=FONT_HEADER_CAPS, fill=(20, 20, 24))
    draw.text((W - 120, y_spec + 88), "#ad", font=FONT_BODY_CLEAN, fill=(160, 150, 140))

    return base.convert("RGB")

# -------------------------------------------------------------
# TEMPLATE 5: Scandinavian Split (Two-Tone Contrast & Feature Bullets)
# -------------------------------------------------------------
def render_scandinavian_split(prod_img, title, board_id, queue_index=1):
    accent = SPLIT_ACCENT_COLORS[queue_index % len(SPLIT_ACCENT_COLORS)]
    bg_top = (245, 242, 236)
    
    base = Image.new("RGBA", (W, H), (*bg_top, 255))
    draw = ImageDraw.Draw(base)
    
    # Top Product Display (0 to 950)
    raw = prod_img.convert("RGBA")
    scale = min(780 / raw.width, 760 / raw.height)
    new_w, new_h = int(raw.width * scale), int(raw.height * scale)
    prod_resized = raw.resize((new_w, new_h), Image.LANCZOS)
    
    # Contact shadow
    c_shadow = Image.new("RGBA", (new_w + 50, 80), (0, 0, 0, 0))
    csdraw = ImageDraw.Draw(c_shadow)
    csdraw.ellipse([25, 15, new_w + 25, 65], fill=(50, 45, 40, 60))
    c_shadow = c_shadow.filter(ImageFilter.GaussianBlur(16))
    
    py = 130 + (780 - new_h) // 2
    base.paste(c_shadow, ((W - new_w - 50) // 2, py + new_h - 40), c_shadow)
    base.paste(prod_resized, ((W - new_w) // 2, py), prod_resized)
    
    # Header above image
    draw.text((65, 50), f"SCANDINAVIAN MODERN // ISSUE {(queue_index % 30) + 1:02d}", font=FONT_HEADER_CAPS, fill=(135, 125, 115))
    draw.text((W - 200, 50), "EDITOR'S PICK", font=FONT_HEADER_CAPS, fill=(170, 120, 60))
    
    # Bottom Contrast Block (950 to 1500)
    split_y = 960
    draw.rectangle([0, split_y, W, H], fill=accent)
    
    # Badge Pill inside bottom block
    badge_text = "VERIFIED AMAZON FIND"
    draw.rounded_rectangle([65, split_y + 45, 65 + 260, split_y + 80], radius=5, fill=(255, 255, 255, 25), outline=(255, 255, 255, 60), width=1)
    draw.text((80, split_y + 52), badge_text, font=FONT_BADGE, fill=(240, 240, 240))
    
    # Title inside bottom block
    clean_title = clean_title_words(title, 55)
    words = clean_title.split()
    line1, line2 = "", ""
    for w in words:
        if len(f"{line1} {w}".strip()) <= 26:
            line1 = f"{line1} {w}".strip()
        else:
            line2 = f"{line2} {w}".strip()
            
    draw.text((65, split_y + 100), line1, font=FONT_TITLE_MED, fill=(255, 255, 255))
    if line2:
        draw.text((65, split_y + 155), line2[:32], font=FONT_TITLE_MED, fill=(255, 255, 255))
        y_bullets = split_y + 225
    else:
        y_bullets = split_y + 175
        
    # Bullet points
    b1 = "✔ Exceptional Customer Reviews & High Ratings"
    b2 = "✔ Timeless Minimalist Aesthetic for Elevated Living"
    draw.text((65, y_bullets), b1, font=FONT_BODY_CLEAN, fill=(225, 220, 215))
    draw.text((65, y_bullets + 38), b2, font=FONT_BODY_CLEAN, fill=(225, 220, 215))
    
    draw.line([(65, y_bullets + 85), (W - 65, y_bullets + 85)], fill=(255, 255, 255, 45), width=1)
    
    # CTA Line
    draw.text((65, y_bullets + 110), "CHECK DETAILS & CURRENT PRICE ON AMAZON ↗", font=FONT_HEADER_CAPS, fill=(255, 255, 255))
    draw.text((W - 120, y_bullets + 112), "#ad", font=FONT_BODY_CLEAN, fill=(190, 185, 180))
    
    return base.convert("RGB")

# -------------------------------------------------------------
# MASTER DYNAMIC ROTATION DISPATCHER (5 DISTINCT TEMPLATES)
# -------------------------------------------------------------
def generate_editorial_pin(product_image_url, title, board_id, queue_index=1):
    """
    True Multi-Template Engine (Rotates across 5 distinct aesthetic layouts):
    1. Editorial Lifestyle (Full-bleed magazine cover)
    2. Studio Flat Lay (Organic linen/travertine with 3D soft contact shadow)
    3. Minimalist Polaroid / Elevated Gallery Frame
    4. Dark Luxury (Deep slate/charcoal with gold glow & accents)
    5. Scandinavian Split (Warm two-tone contrast block with feature bullets)
    """
    resp = requests.get(product_image_url, timeout=15)
    prod_img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    
    is_white = is_image_white_cutout(prod_img)
    
    # 5-way rotation cycle based on queue_index
    cycle = queue_index % 5
    
    if not is_white:
        # For natural scene/lifestyle images:
        if cycle in [0, 3]:
            img = render_editorial_lifestyle(prod_img, title, board_id, queue_index)
            return img, "Editorial [Lifestyle Scene]"
        elif cycle in [1, 4]:
            img = render_polaroid_gallery(prod_img, title, board_id, queue_index)
            return img, "Editorial [Polaroid Gallery]"
        else:
            img = render_dark_luxury(prod_img, title, board_id, queue_index)
            return img, "Editorial [Dark Luxury]"
    else:
        # For white-cutout product images:
        if cycle == 0:
            img = render_studio_flatlay(prod_img, title, board_id, queue_index)
            return img, "Editorial [Studio Flat Lay]"
        elif cycle == 1:
            img = render_polaroid_gallery(prod_img, title, board_id, queue_index)
            return img, "Editorial [Polaroid Gallery]"
        elif cycle == 2:
            img = render_scandinavian_split(prod_img, title, board_id, queue_index)
            return img, "Editorial [Scandinavian Split]"
        elif cycle == 3:
            img = render_dark_luxury(prod_img, title, board_id, queue_index)
            return img, "Editorial [Dark Luxury]"
        else:
            img = render_studio_flatlay(prod_img, title, board_id, queue_index)
            return img, "Editorial [Studio Flat Lay]"
