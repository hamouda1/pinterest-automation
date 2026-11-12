import sys
import io
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

FONTS_DIR_CANDIDATE = Path(__file__).resolve().parent / "fonts"
FONT_DIR = FONTS_DIR_CANDIDATE if FONTS_DIR_CANDIDATE.exists() else Path(r"C:\Windows\Fonts")

def _get_font(filename, size):
    return ImageFont.truetype(str(FONT_DIR / filename), size)

FONT_TITLE_SERIF = _get_font("georgiab.ttf", 36)
FONT_SUB_SERIF = _get_font("georgia.ttf", 20)
FONT_SUB_ITALIC = _get_font("georgia.ttf", 19)
FONT_SANS_BOLD = _get_font("segoeuib.ttf", 21)
FONT_SANS_MED = _get_font("segoeuib.ttf", 15)
FONT_SANS_SMALL = _get_font("segoeuib.ttf", 13)
FONT_SANS_REG = _get_font("segoeui.ttf", 15)
FONT_STARS = _get_font("segoeui.ttf", 22)

# Text Wrapping Helper
def draw_safe_text(draw, text, font, fill, max_width, start_x, start_y, line_spacing=6, align="center"):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bb = font.getbbox(test_line)
        if (bb[2] - bb[0]) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))

    cur_y = start_y
    for line in lines:
        bb = font.getbbox(line)
        lw = bb[2] - bb[0]
        lh = bb[3] - bb[1]
        if align == "center":
            lx = start_x + (max_width - lw) // 2
        elif align == "right":
            lx = start_x + max_width - lw
        else:
            lx = start_x
        draw.text((lx, cur_y), line, font=font, fill=fill)
        cur_y += lh + line_spacing
    return cur_y

def clean_title(title, max_chars=36):
    t = title.split(" | ")[0].strip()
    if len(t) > max_chars:
        t = t[:max_chars].rsplit(" ", 1)[0]
    return t

def draw_luxury_button(base, draw, y, text, fill, text_color=(255, 255, 255, 255), W=1000):
    btn_w, btn_h = 520, 68
    bx = (W - btn_w) // 2
    b_shadow = Image.new("RGBA", (btn_w + 30, btn_h + 30), (0, 0, 0, 0))
    ImageDraw.Draw(b_shadow).rounded_rectangle([15, 15 + 4, 15 + btn_w, 15 + btn_h + 4], radius=34, fill=(0, 0, 0, 40))
    base.alpha_composite(b_shadow.filter(ImageFilter.GaussianBlur(8)), (bx - 15, y - 15))
    
    draw.rounded_rectangle([bx, y, bx + btn_w, y + btn_h], radius=34, fill=fill)
    c_bb = FONT_SANS_BOLD.getbbox(text)
    tw = c_bb[2] - c_bb[0]
    draw.text((bx + (btn_w - tw)//2, y + 20), text, font=FONT_SANS_BOLD, fill=text_color)

def draw_ftc(draw, y, W=1000, color=(140, 120, 105, 255)):
    ftc = "As an Amazon Associate I earn from qualifying purchases • #ad"
    bb = FONT_SANS_REG.getbbox(ftc)
    draw.text(((W - (bb[2]-bb[0]))//2, y), ftc, font=FONT_SANS_REG, fill=color)

# -------------------------------------------------------------
# 1. Fall Template: Cozy Sweater Weather (الكنزات الدافئة والكراميل)
# -------------------------------------------------------------
def template_fall_sweater_weather(prod_img, title, board_id="1093037840753522206"):
    W, H = 1000, 1500
    t = clean_title(title)
    
    # Warm Caramel & Golden Honey Gradient
    base = Image.new("RGBA", (W, H), (246, 238, 226, 255))
    draw = ImageDraw.Draw(base)
    for y in range(H):
        ratio = y / H
        r = int(248 - 18 * ratio)
        g = int(238 - 25 * ratio)
        b = int(224 - 32 * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # Copper Inset Border
    draw.rounded_rectangle([35, 35, W - 35, H - 35], radius=22, outline=(195, 130, 85, 255), width=2)
    draw.rounded_rectangle([42, 42, W - 42, H - 42], radius=18, outline=(225, 185, 150, 255), width=1)

    # Fall Badge
    badge_text = "🍂 SWEATER WEATHER ESSENTIAL 🍂"
    b_bb = FONT_SANS_SMALL.getbbox(badge_text)
    bw = b_bb[2] - b_bb[0] + 36
    draw.rounded_rectangle([(W - bw)//2, 65, (W + bw)//2, 98], radius=16, fill=(160, 68, 38, 255))
    draw.text(((W - (b_bb[2]-b_bb[0]))//2, 72), badge_text, font=FONT_SANS_SMALL, fill=(255, 245, 235, 255))

    draw_safe_text(draw, t, FONT_TITLE_SERIF, (45, 32, 24, 255), 840, 80, 115)
    draw_safe_text(draw, "Plush Cozy Comfort for Crisp Autumn Days", FONT_SUB_SERIF, (140, 80, 45, 255), 840, 80, 168)

    # Floating Card with Soft Warm Shadow
    card_w, card_h = 820, 860
    cx, cy = (W - card_w)//2, 225
    shadow = Image.new("RGBA", (card_w + 50, card_h + 50), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([25, 30, 25 + card_w, 30 + card_h], radius=26, fill=(80, 40, 20, 35))
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(16)), (cx - 25, cy - 25))

    card = Image.new("RGBA", (card_w, card_h), (255, 254, 250, 255))
    c_draw = ImageDraw.Draw(card)
    c_draw.rounded_rectangle([0, 0, card_w, card_h], radius=24, outline=(238, 225, 208, 255), width=2)
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))

    draw.text((cx + 175, 1125), "★★★★★", font=FONT_STARS, fill=(230, 140, 35, 255))
    draw.text((cx + 300, 1128), "Top Rated Cozy Autumn Favorite", font=FONT_SANS_MED, fill=(90, 55, 35, 255))
    
    # Burnt Cinnamon Button
    draw_luxury_button(base, draw, 1180, "CHECK SIZES & COLORS ON AMAZON ↗", (165, 68, 38, 255))
    draw_ftc(draw, 1270, color=(140, 110, 90, 255))
    return base.convert("RGB")

# -------------------------------------------------------------
# 2. Fall Template: Warm Terracotta & Maple (الصلصال والقرفة الخريفية)
# -------------------------------------------------------------
def template_fall_terracotta_maple(prod_img, title, board_id="1093037840753522209"):
    W, H = 1000, 1500
    t = clean_title(title)
    
    # Rich Terracotta / Clay Autumn Tone
    base = Image.new("RGBA", (W, H), (195, 102, 74, 255))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([35, 35, W - 35, H - 35], radius=24, outline=(245, 215, 195, 255), width=2)

    draw.text((70, 65), "🍁 THE COZY FALL CAPSULE // 2026 🍁", font=FONT_SANS_SMALL, fill=(255, 240, 225, 255))
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (255, 255, 255, 255), 860, 70, 95, align="left")
    draw_safe_text(draw, "Pair with Knit Scarves, Denim & Autumn Ankle Boots", FONT_SUB_SERIF, (250, 220, 205, 255), 860, 70, 145, align="left")

    card_w, card_h = 860, 850
    cx, cy = 70, 215
    card = Image.new("RGBA", (card_w, card_h), (255, 253, 248, 255))
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))

    draw.text((cx + 190, 1110), "★★★★★", font=FONT_STARS, fill=(255, 245, 220, 255))
    draw.text((cx + 315, 1113), "4.9 ★ Rated For Crisp Fall Days", font=FONT_SANS_MED, fill=(255, 240, 225, 255))
    
    # Dark Chestnut Button
    draw_luxury_button(base, draw, 1165, "CHECK CURRENT PRICE ON AMAZON ↗", (65, 32, 22, 255))
    draw_ftc(draw, 1260, color=(245, 215, 200, 255))
    return base.convert("RGB")

# -------------------------------------------------------------
# 3. Fall Template: Dark Chestnut & Pumpkin Spice (الكستناء والموكا الداكنة)
# -------------------------------------------------------------
def template_fall_chestnut_mocha(prod_img, title, board_id="1093037840753522206"):
    W, H = 1000, 1500
    t = clean_title(title).upper()
    
    # Deep Roasted Chestnut & Dark Espresso
    base = Image.new("RGBA", (W, H), (32, 20, 15, 255))
    draw = ImageDraw.Draw(base)

    draw.line([(60, 60), (W - 60, 60)], fill=(85, 55, 45, 255), width=1)
    draw.text((60, 70), "AUTUMN / WINTER 2026 // COZY EDIT", font=FONT_SANS_SMALL, fill=(225, 150, 75, 255))
    draw.text((W - 220, 70), "FALL ESSENTIAL", font=FONT_SANS_SMALL, fill=(200, 160, 140, 255))
    draw.line([(60, 95), (W - 60, 95)], fill=(85, 55, 45, 255), width=1)

    draw_safe_text(draw, t, FONT_TITLE_SERIF, (255, 250, 245, 255), 880, 60, 115, align="left")
    draw.text((60, 165), "WARM COZY ESSENTIAL • CRISP WEATHER READY", font=FONT_SANS_SMALL, fill=(225, 150, 75, 255))

    card_w, card_h = 880, 860
    cx, cy = 60, 215
    draw.rectangle([cx, cy, cx + card_w, cy + card_h], fill=(255, 255, 255, 255))
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    base.alpha_composite(p, (cx + (card_w - p.width)//2, cy + (card_h - p.height)//2))

    draw.line([(60, 1115), (W - 60, 1115)], fill=(85, 55, 45, 255), width=1)
    draw.text((60, 1125), "★ ★ ★ ★ ★  TOP RATED COZY LAYER ON AMAZON", font=FONT_SANS_SMALL, fill=(230, 140, 35, 255))
    draw.text((W - 260, 1125), "FALL FAVORITE", font=FONT_SANS_SMALL, fill=(190, 150, 130, 255))

    # Warm Pumpkin Amber Button
    draw_luxury_button(base, draw, 1175, "SHOP THE FALL PIECE ON AMAZON ↗", (215, 125, 45, 255), text_color=(32, 20, 15, 255))
    draw_ftc(draw, 1270, color=(160, 130, 115, 255))
    return base.convert("RGB")

# -------------------------------------------------------------
# 4. Fall Template: Oatmeal & Golden Foliage (الشوفان والدفء الخريفي)
# -------------------------------------------------------------
def template_fall_oatmeal_foliage(prod_img, title, board_id="1093037840753522205"):
    W, H = 1000, 1500
    t = clean_title(title)
    
    # Cozy Warm Oatmeal / Flannel Tone
    base = Image.new("RGBA", (W, H), (247, 242, 234, 255))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([35, 35, W - 35, H - 35], radius=18, outline=(220, 205, 185, 255), width=1)

    draw.text((65, 65), "✨ COZY FALL COLLECTION ✨", font=FONT_SANS_SMALL, fill=(150, 90, 45, 255))
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (40, 32, 26, 255), 870, 65, 95, align="left")
    draw_safe_text(draw, "Essential Autumn Silhouette • Comfortable Everyday Layering", FONT_SUB_SERIF, (120, 105, 90, 255), 870, 65, 145, align="left")

    card_w, card_h = 870, 770
    cx, cy = 65, 195
    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    c_draw = ImageDraw.Draw(card)
    c_draw.rounded_rectangle([0, 0, card_w, card_h], radius=18, outline=(235, 225, 210, 255), width=1)
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))

    # Fall checklist
    draw.line([(65, 1000), (W - 65, 1000)], fill=(220, 205, 185, 255), width=1)
    draw.text((65, 1020), "🍂 Ultra-Soft Warm Layering", font=FONT_SANS_MED, fill=(60, 48, 38, 255))
    draw.text((365, 1020), "🍂 Breathable for Crisp Days", font=FONT_SANS_MED, fill=(60, 48, 38, 255))
    draw.text((675, 1020), "🍂 Top 5★ Verified", font=FONT_SANS_MED, fill=(60, 48, 38, 255))
    draw.line([(65, 1060), (W - 65, 1060)], fill=(220, 205, 185, 255), width=1)

    draw.text((65, 1090), "★★★★★  Highly Rated For Cozy Autumn Weather", font=FONT_SANS_MED, fill=(195, 110, 40, 255))
    
    # Warm Deep Olive / Forest Moss Button
    draw_luxury_button(base, draw, 1165, "CHECK AVAILABILITY ON AMAZON ↗", (72, 85, 60, 255))
    draw_ftc(draw, 1260, color=(140, 125, 110, 255))
    return base.convert("RGB")

FALL_TEMPLATES_LIST = [
    ("Cozy Sweater Weather", template_fall_sweater_weather),
    ("Warm Terracotta Maple", template_fall_terracotta_maple),
    ("Dark Chestnut Mocha", template_fall_chestnut_mocha),
    ("Oatmeal Golden Foliage", template_fall_oatmeal_foliage)
]

if __name__ == "__main__":
    test_img_url = "https://m.media-amazon.com/images/I/811O9zF0kZL.jpg"
    print("Testing and rendering all 4 dedicated Autumn / Fall templates...")
    resp = requests.get(test_img_url, timeout=15)
    p_img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    
    for idx, (t_name, t_fn) in enumerate(FALL_TEMPLATES_LIST):
        img = t_fn(p_img, "Oversized Cable Knit Fall Sweater")
        out = f"fall_template_{idx+1}.jpg"
        img.save(out, quality=95)
        print(f"✔ Rendered Fall Template #{idx+1}: {t_name} -> {out}")
