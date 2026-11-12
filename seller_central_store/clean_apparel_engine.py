"""
Masterpiece Editorial Apparel Pin Rendering Engine (FW 2026-2027 Luxury Edition)
==============================================================================
Pure Studio Lighting • 3-Layer Physical Contact Shadows • Cinzel Roman Typography
100% Clean: No Tofu Boxes, No Corner Diamonds, No Misaligned Header Text, No Prime/Return Text.
"""

import os
import sys
import tempfile
import time
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1000, 1500

# Fonts Directory
FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"
if not FONTS_DIR.exists():
    FONTS_DIR = Path(r"C:\Users\KIZMO STORE\Documents\pinterest\canva_products\fonts")
CINZEL_FONT_PATH = FONTS_DIR / "Cinzel-Regular.ttf"

# Load Fonts safely with robust fallbacks
font_title_master = ImageFont.truetype(str(CINZEL_FONT_PATH), 48)
try:
    font_sub = ImageFont.truetype(str(FONTS_DIR / "georgiai.ttf"), 29)      # Romantic Georgia Italic
    font_spec = ImageFont.truetype(str(FONTS_DIR / "georgia.ttf"), 21)
    font_caps = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 14)
    font_cta = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 18)
    font_arrow = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 24)
except Exception:
    font_sub = ImageFont.truetype("timesi.ttf", 29)
    font_spec = ImageFont.truetype("times.ttf", 21)
    font_caps = ImageFont.truetype("arial.ttf", 14)
    font_cta = ImageFont.truetype("arial.ttf", 18)
    font_arrow = ImageFont.truetype("arial.ttf", 24)

# 8 Official Masterpiece Palettes (Autumn/Winter 2026-2027)
MASTERPIECE_PALETTES = [
    {
        "id": "earthy_rust",
        "name": "Earthy Terracotta Rust",
        "name_ar": "الصدأ والآجر الترابي الخريفي",
        "bg_card": (148, 54, 22),         # Terracotta Rust / Fallen Leaves
        "badge_color": (255, 225, 200),   # Apricot Cream
        "title_color": (255, 255, 255),   # Crisp Silk White
        "sub_color": (250, 230, 215),     # Soft Peach
        "accent_line": (212, 175, 122),   # Champagne Gold
        "cta_bg": (255, 255, 255),        # Pure White
        "cta_text": (140, 48, 18),        # Rust Text
        "cta_border": (218, 185, 135),    # Gold border
        "arrow_color": (148, 54, 22),
        "eyebrow_badge": "AUTUMN / WINTER 2026 EDITORIAL"
    },
    {
        "id": "chocolate_brown",
        "name": "Rich Chocolate Brown",
        "name_ar": "بني الشوكولاتة الغني",
        "bg_card": (54, 32, 22),          # Deep Dark Chocolate
        "badge_color": (225, 175, 125),   # Caramel Gold
        "title_color": (245, 242, 235),   # Cloud Dancer White
        "sub_color": (230, 215, 200),     # Soft Cream
        "accent_line": (212, 175, 122),   # Champagne Gold
        "cta_bg": (250, 248, 242),        # Warm Ivory
        "cta_text": (54, 32, 22),         # Chocolate Text
        "cta_border": (218, 185, 135),    # Gold border
        "arrow_color": (166, 124, 82),
        "eyebrow_badge": "WARM LUXURY EDIT • CHOCOLATE"
    },
    {
        "id": "warm_caramel",
        "name": "Warm Caramel",
        "name_ar": "الكراميل والعسل الدافئ",
        "bg_card": (158, 98, 55),         # Golden Warm Caramel
        "badge_color": (255, 240, 215),   # Soft Vanilla
        "title_color": (255, 255, 255),   # Pure White
        "sub_color": (250, 225, 200),     # Whipped Caramel
        "accent_line": (255, 230, 195),   # Vanilla Gold
        "cta_bg": (255, 255, 255),        # Pure White
        "cta_text": (140, 75, 30),        # Caramel Text
        "cta_border": (235, 195, 145),    # Gold border
        "arrow_color": (158, 98, 55),
        "eyebrow_badge": "COZY NOVEMBER VIBES • CARAMEL"
    },
    {
        "id": "deep_burgundy",
        "name": "Deep Royal Burgundy",
        "name_ar": "العنابي والبرغندي الملكي",
        "bg_card": (72, 16, 28),          # Regal Wine Burgundy
        "badge_color": (245, 205, 212),   # Cashmere Blush Rose
        "title_color": (250, 245, 240),   # Cloud Dancer White
        "sub_color": (240, 220, 225),     # Soft Rose Cream
        "accent_line": (212, 175, 122),   # Champagne Gold
        "cta_bg": (252, 248, 246),        # Rose Ivory
        "cta_text": (72, 16, 28),         # Burgundy Text
        "cta_border": (218, 185, 135),    # Gold border
        "arrow_color": (185, 95, 110),
        "eyebrow_badge": "HAUTE COUTURE EDIT • BURGUNDY"
    },
    {
        "id": "olive_green",
        "name": "Botanical Olive Green",
        "name_ar": "الأخضر الزيتوني النباتي",
        "bg_card": (56, 68, 46),          # Sophisticated Botanical Olive
        "badge_color": (215, 230, 205),   # Sage Dew
        "title_color": (250, 248, 242),   # Cloud Dancer White
        "sub_color": (228, 238, 222),     # Soft Eucalyptus
        "accent_line": (212, 175, 122),   # Champagne Gold
        "cta_bg": (250, 248, 242),        # Pale Sage Ivory
        "cta_text": (48, 62, 38),         # Olive Text
        "cta_border": (218, 185, 135),    # Gold border
        "arrow_color": (85, 105, 75),
        "eyebrow_badge": "BOTANICAL HARMONY • OLIVE GREEN"
    },
    {
        "id": "navy_blue",
        "name": "Parisian Midnight Navy",
        "name_ar": "الأزرق الكحلي الباريسي الكلاسيكي",
        "bg_card": (20, 32, 52),          # Parisian Midnight Navy
        "badge_color": (230, 200, 160),   # Warm Caramel Accent
        "title_color": (250, 248, 245),   # Cloud Dancer
        "sub_color": (220, 228, 240),     # Pale Chambray
        "accent_line": (212, 175, 122),   # Champagne Gold
        "cta_bg": (250, 248, 245),        # Cloud Dancer White
        "cta_text": (20, 32, 52),         # Navy Text
        "cta_border": (218, 185, 135),    # Gold border
        "arrow_color": (180, 140, 95),
        "eyebrow_badge": "TIMELESS CLASSIC • NAVY BLUE"
    },
    {
        "id": "cloud_dancer",
        "name": "Pantone 2026 Cloud Dancer",
        "name_ar": "كلود دانسر (لون عام 2026 من بانتون)",
        "bg_card": (238, 234, 226),       # Pantone 11-4201 Cloud Dancer
        "badge_color": (148, 54, 22),     # Rust contrast accent
        "title_color": (54, 32, 22),      # Deep Chocolate Brown
        "sub_color": (90, 68, 55),        # Warm Muted Espresso
        "accent_line": (185, 155, 125),   # Soft Warm Stone
        "cta_bg": (54, 32, 22),           # Chocolate Button
        "cta_text": (245, 242, 235),      # Cloud Dancer White text
        "cta_border": (185, 155, 125),    # Warm Stone border
        "arrow_color": (218, 185, 135),
        "eyebrow_badge": "PANTONE COLOR OF THE YEAR 2026"
    },
    {
        "id": "alpine_slate",
        "name": "Alpine Forest Slate",
        "name_ar": "أردواز الغابات الألبية الفاخر",
        "bg_card": (24, 28, 26),          # Deep Alpine Forest Slate
        "badge_color": (212, 175, 122),   # Champagne Gold
        "title_color": (250, 248, 242),   # Pure Silk White
        "sub_color": (205, 196, 185),     # Soft Oatmeal
        "accent_line": (212, 175, 122),   # Champagne Gold
        "cta_bg": (252, 249, 244),        # Travertine Cream
        "cta_text": (28, 22, 18),         # Espresso Text
        "cta_border": (218, 185, 135),    # Gold border
        "arrow_color": (185, 142, 92),
        "eyebrow_badge": "THE 2026 MOUNTAIN COLLECTION"
    }
]

def draw_tracked_text(draw, pos, text, font, fill, tracking=2, anchor="mm"):
    chars = list(text)
    total_w = sum(draw.textbbox((0, 0), c, font=font)[2] for c in chars) + (len(chars) - 1) * tracking
    bbox = draw.textbbox((0, 0), text, font=font)
    total_h = bbox[3] - bbox[1]
    
    x, y = pos
    if anchor == "mm":
        start_x = x - total_w // 2
        start_y = y - total_h // 2
    elif anchor == "lm":
        start_x = x
        start_y = y - total_h // 2
    elif anchor == "rm":
        start_x = x - total_w
        start_y = y - total_h // 2
    else:
        start_x = x
        start_y = y
        
    cur_x = start_x
    for c in chars:
        draw.text((cur_x, start_y), c, font=font, fill=fill)
        c_w = draw.textbbox((0, 0), c, font=font)[2]
        cur_x += c_w + tracking

def fetch_image(source):
    if isinstance(source, Image.Image):
        return source.convert("RGBA")
    if isinstance(source, (str, Path)):
        p = Path(source)
        if p.exists():
            return Image.open(str(p)).convert("RGBA")
        if str(source).startswith("http://") or str(source).startswith("https://"):
            tmp_path = os.path.join(tempfile.gettempdir(), f"img_{os.getpid()}_{int(time.time()*1000)}.jpg")
            cmd = ["curl.exe", "-s", "-L", "--retry", "3", str(source), "-A", "Mozilla/5.0", "-o", tmp_path]
            res = subprocess.run(cmd, timeout=25)
            if res.returncode == 0 and os.path.exists(tmp_path):
                img = Image.open(tmp_path).convert("RGBA")
                try: os.remove(tmp_path)
                except Exception: pass
                return img
    raise ValueError(f"Unsupported image source: {source}")

def fit_cinzel_title(text, max_w=860):
    words = text.split()
    if len(words) >= 4 and len(text) > 28:
        mid = len(words) // 2
        l1 = " ".join(words[:mid])
        l2 = " ".join(words[mid:])
        font = ImageFont.truetype(str(CINZEL_FONT_PATH), 42)
        return [l1, l2], font
    font = ImageFont.truetype(str(CINZEL_FONT_PATH), 46)
    return [text], font

def render_masterpiece_pin(img_source, title, subtitle=None, palette="auto", eyebrow=None):
    """
    Renders an Ultra-Luxury Masterpiece Apparel Pin for Pinterest (1000 x 1500 px).
    - Travertine luxury studio lighting with directional 45-degree sunlight beam.
    - 3-Layer physical studio shadow (Umbra, Penumbra, Ambient Occlusion).
    - Clean 1px studio margin (NO corner diamonds/squares).
    - Pristine top space with generous breathing room.
    - Cinzel Roman luxury title with subpixel tracking.
    - Romantic Georgia italic subtitle.
    - Clean hairline divider (NO center diamonds/squares).
    - Luxury pill CTA button with clean chevron '>' (NO tofu missing box).
    - Strictly zero delivery / return text.
    """
    # 1. Determine Palette
    if isinstance(palette, int):
        p = MASTERPIECE_PALETTES[palette % len(MASTERPIECE_PALETTES)]
    elif isinstance(palette, str) and palette != "auto":
        p = next((x for x in MASTERPIECE_PALETTES if x["id"] == palette), MASTERPIECE_PALETTES[0])
    else:
        # Automatic Niche Matching
        t_low = title.lower()
        if any(w in t_low for w in ["thanksgiving", "autumn", "fall", "pumpkin", "maple", "harvest"]):
            p = MASTERPIECE_PALETTES[0] # Earthy Rust
        elif any(w in t_low for w in ["mountain", "hiking", "trail", "cascade", "nature", "outdoor"]):
            p = MASTERPIECE_PALETTES[7] # Alpine Slate
        elif any(w in t_low for w in ["retro", "vintage", "90s", "camping"]):
            p = MASTERPIECE_PALETTES[4] # Olive Green
        elif any(w in t_low for w in ["coffee", "skeleton", "streetwear"]):
            p = MASTERPIECE_PALETTES[1] # Rich Chocolate Brown
        elif any(w in t_low for w in ["christmas", "holiday", "wine"]):
            p = MASTERPIECE_PALETTES[3] # Deep Burgundy
        else:
            p = MASTERPIECE_PALETTES[1] # Chocolate Brown default

    # 2. Build Multi-Stop Photorealistic Travertine Studio Canvas
    canvas = Image.new("RGBA", (W, H), (252, 249, 244, 255))
    cdraw = ImageDraw.Draw(canvas)

    for r_step in range(45):
        factor = r_step / 45.0
        cr = int(252 - factor * 26)
        cg = int(249 - factor * 32)
        cb = int(244 - factor * 40)
        inset_x = int(factor * 190)
        inset_y = int(factor * 270)
        cdraw.rectangle([inset_x, inset_y, W - inset_x, H - inset_y], outline=(cr, cg, cb, 35), width=6)

    canvas = canvas.filter(ImageFilter.GaussianBlur(16))

    # Directional Studio Softbox Sunlight Beam (Top-Left 45 degrees)
    sunlight = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sunlight)
    sdraw.polygon([(-100, -100), (600, -100), (W + 200, 900), (-100, 700)], fill=(255, 250, 238, 45))
    sunlight = sunlight.filter(ImageFilter.GaussianBlur(70))
    canvas = Image.alpha_composite(canvas, sunlight)

    # Clean 1px Studio Margin (Pure Line, NO Corner Diamonds)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([25, 25, W - 25, H - 25], outline=(175, 155, 132, 120), width=1)

    # 3. Product Hero with 3-Layer Physical Studio Shadow
    prod_raw = fetch_image(img_source)
    scale = min(820 / prod_raw.width, 820 / prod_raw.height)
    new_w, new_h = int(prod_raw.width * scale), int(prod_raw.height * scale)
    prod_resized = prod_raw.resize((new_w, new_h), Image.LANCZOS)

    prod_x = (W - new_w) // 2
    prod_y = 135 + (800 - new_h) // 2
    prod_base_y = prod_y + new_h

    # Layer 1: Ambient Occlusion
    ao_shadow = Image.new("RGBA", (new_w + 140, 150), (0, 0, 0, 0))
    ImageDraw.Draw(ao_shadow).ellipse([20, 20, new_w + 120, 130], fill=(50, 38, 28, 55))
    ao_shadow = ao_shadow.filter(ImageFilter.GaussianBlur(32))
    canvas.paste(ao_shadow, (prod_x - 70, prod_base_y - 75), ao_shadow)

    # Layer 2: Directional Cast Shadow
    dir_shadow = Image.new("RGBA", (new_w + 60, 90), (0, 0, 0, 0))
    ImageDraw.Draw(dir_shadow).ellipse([25, 20, new_w + 45, 75], fill=(45, 32, 22, 95))
    dir_shadow = dir_shadow.filter(ImageFilter.GaussianBlur(16))
    canvas.paste(dir_shadow, (prod_x - 10, prod_base_y - 48), dir_shadow)

    # Layer 3: Tight Ground Contact Shadow (Umbra)
    umbra_shadow = Image.new("RGBA", (int(new_w * 0.72), 34), (0, 0, 0, 0))
    ImageDraw.Draw(umbra_shadow).ellipse([8, 6, int(new_w * 0.72) - 8, 28], fill=(25, 18, 12, 175))
    umbra_shadow = umbra_shadow.filter(ImageFilter.GaussianBlur(6))
    canvas.paste(umbra_shadow, (prod_x + int(new_w * 0.14), prod_base_y - 18), umbra_shadow)

    # Paste Crisp Product (No clutter in upper area)
    canvas.paste(prod_resized, (prod_x, prod_y), prod_resized)

    # 4. Bottom Haute Editorial Typography Card
    card_top = 955
    card = Image.new("RGBA", (W, H - card_top), (*p["bg_card"], 255))
    cdraw = ImageDraw.Draw(card)

    # Clean Accent Line at Top of Card
    cdraw.line([0, 0, W, 0], fill=(*p["accent_line"], 200), width=1)

    # Card Drop-Shadow onto upper travertine canvas
    card_shadow = Image.new("RGBA", (W, 45), (0, 0, 0, 0))
    ImageDraw.Draw(card_shadow).rectangle([0, 15, W, 45], fill=(0, 0, 0, 95))
    card_shadow = card_shadow.filter(ImageFilter.GaussianBlur(14))
    canvas.paste(card_shadow, (0, card_top - 30), card_shadow)
    canvas.paste(card, (0, card_top), card)

    # Typography
    draw = ImageDraw.Draw(canvas)

    # (A) Curation Eyebrow Badge
    badge_str = eyebrow or p["eyebrow_badge"]
    draw_tracked_text(draw, (W // 2, card_top + 55), badge_str, font_caps, p["badge_color"], tracking=4, anchor="mm")

    # (B) Main Title (Cinzel Roman Serif)
    clean_title = title.split("Graphic Art")[0].split("Merchandise")[0].split("Graphic T-Shirt")[0].strip().rstrip("-").strip()
    title_lines, font_t = fit_cinzel_title(clean_title)

    if len(title_lines) == 1:
        draw_tracked_text(draw, (W // 2, card_top + 130), title_lines[0].upper(), font_t, p["title_color"], tracking=3, anchor="mm")
        y_sub = card_top + 205
    else:
        draw_tracked_text(draw, (W // 2, card_top + 110), title_lines[0].upper(), font_t, p["title_color"], tracking=3, anchor="mm")
        draw_tracked_text(draw, (W // 2, card_top + 160), title_lines[1].upper(), font_t, p["title_color"], tracking=3, anchor="mm")
        y_sub = card_top + 215

    # (C) Romantic Subtitle with Italic Grace
    sub_str = subtitle or "100% Breathable Cotton   •   Sizes S to 3XL"
    draw.text((W // 2, y_sub), sub_str, font=font_sub, fill=p["sub_color"], anchor="mm")

    # (D) Clean Pure Hairline Divider (NO diamond, NO squares)
    y_div = y_sub + 55
    div_w = 340
    draw.line([(W // 2 - div_w // 2, y_div), (W // 2 + div_w // 2, y_div)], fill=(*p["accent_line"], 120), width=1)

    # (E) Luxury Pill Button
    btn_w, btn_h = 520, 82
    btn_x = (W - btn_w) // 2
    btn_y = y_div + 55

    # Button Multi-layer Ambient Shadow
    btn_shadow = Image.new("RGBA", (btn_w + 45, btn_h + 45), (0, 0, 0, 0))
    ImageDraw.Draw(btn_shadow).rounded_rectangle([20, 20, 20 + btn_w, 20 + btn_h], radius=41, fill=(0, 0, 0, 160))
    btn_shadow = btn_shadow.filter(ImageFilter.GaussianBlur(16))
    canvas.paste(btn_shadow, (btn_x - 20, btn_y - 10), btn_shadow)

    # Button Body
    btn = Image.new("RGBA", (btn_w, btn_h), (*p["cta_bg"], 255))
    bdraw = ImageDraw.Draw(btn)
    bdraw.rounded_rectangle([0, 0, btn_w - 1, btn_h - 1], radius=41, outline=(*p["cta_border"], 255), width=2)

    # Button text and chevron '>'
    draw_tracked_text(bdraw, (btn_w // 2 - 15, btn_h // 2), "DISCOVER ON AMAZON", font_cta, p["cta_text"], tracking=4, anchor="mm")
    bdraw.text((btn_w - 65, btn_h // 2), ">", font=font_arrow, fill=p["arrow_color"], anchor="mm")

    bmask = Image.new("L", (btn_w, btn_h), 0)
    ImageDraw.Draw(bmask).rounded_rectangle([0, 0, btn_w, btn_h], radius=41, fill=255)
    canvas.paste(btn, (btn_x, btn_y), bmask)

    # (F) Micro-Footer under button
    draw_tracked_text(draw, (W // 2, btn_y + btn_h + 38), "CURATED AMAZON FIND  •  DIRECT VERIFIED PRODUCT", font_caps, p["badge_color"], tracking=2, anchor="mm")

    return canvas.convert("RGB")
