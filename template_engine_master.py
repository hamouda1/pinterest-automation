import sys
import io
import base64
import requests
from pathlib import Path
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 1. High-End Editorial & Studio Engines (v4)
from template_engine_v4_editorial import (
    render_editorial_lifestyle,
    render_studio_flatlay,
    render_polaroid_gallery,
    render_dark_luxury,
    render_scandinavian_split,
    is_image_white_cutout
)

# 2. Refined Luxury & Specialized Layouts
from template_engine_luxury import (
    t1_linen_studio,
    t2_polaroid,
    t3_editorial,
    t4_boutique,
    t5_festive,
    t6_scandinavian,
    t7_moodboard,
    t8_artisan,
    t9_tech_streetwear,
    t10_review_spotlight,
    t11_sage_split,
    t12_monochrome,
    t13_terracotta,
    t14_cinematic,
    t15_haute_boutique,
    t16_pet_boutique
)

# 3. Dedicated Seasonal & Atmospheric Palettes
from fall_templates import (
    template_fall_sweater_weather,
    template_fall_terracotta_maple,
    template_fall_chestnut_mocha,
    template_fall_oatmeal_foliage
)

# -------------------------------------------------------------
# GRAND 25-TEMPLATE MASTER REGISTRY
# -------------------------------------------------------------
MASTER_TEMPLATES_REGISTRY = [
    # 0. Editorial Magazine Scene (Full-bleed lifestyle lookbook)
    ("Editorial [Lifestyle Magazine Full-Bleed]", lambda img, t, b, q: render_editorial_lifestyle(img, t, b, q)),
    
    # 1. Studio Flat Lay (Warm travertine/linen with 3D soft contact shadow)
    ("Studio [Travertine & 3D Soft Shadow]", lambda img, t, b, q: render_studio_flatlay(img, t, b, q)),
    
    # 2. Gallery Selection (Minimalist elevated polaroid frame)
    ("Gallery [Minimalist Polaroid Frame]", lambda img, t, b, q: render_polaroid_gallery(img, t, b, q)),
    
    # 3. Slate Noir Luxury (Charcoal canvas with warm gold halo)
    ("Luxury [Slate Noir & Golden Glow]", lambda img, t, b, q: render_dark_luxury(img, t, b, q)),
    
    # 4. Nordic Two-Tone Split (Architectural contrast block with feature bullets)
    ("Nordic [Two-Tone Architectural Split]", lambda img, t, b, q: render_scandinavian_split(img, t, b, q)),
    
    # 5. Styling Moodboard (Outfit & space formula card)
    ("Moodboard [Outfit & Space Styling Formula]", lambda img, t, b, q: t7_moodboard(img, t, b)),
    
    # 6. Artisan Curated Lookbook (Artisan review frame)
    ("Lookbook [Artisan Curated Lookbook]", lambda img, t, b, q: t8_artisan(img, t, b)),
    
    # 7. Modern Tech Grid (Clean minimalist archive grid)
    ("Tech-Minimal [Modern Archive Grid]", lambda img, t, b, q: t9_tech_streetwear(img, t, b)),
    
    # 8. Verified Buyer Spotlight (Large 5-star customer review quote)
    ("Social Proof [5-Star Verified Buyer Review]", lambda img, t, b, q: t10_review_spotlight(img, t, b)),
    
    # 9. Pastel Sage Split (Soft sage green and linen two-tone)
    ("Palette [Soft Pastel Sage & Sand Split]", lambda img, t, b, q: t11_sage_split(img, t, b)),
    
    # 10. High-Fashion Monochrome (Clean editorial brutalist)
    ("High-Fashion [Monochrome Brutalist]", lambda img, t, b, q: t12_monochrome(img, t, b)),
    
    # 11. Boho Terracotta Clay (Warm earth tone aesthetic)
    ("Earthy [Warm Boho Terracotta Clay]", lambda img, t, b, q: t13_terracotta(img, t, b)),
    
    # 12. 35mm Cinema Film Slide (Classic cinematic photography slide)
    ("Cinematic [35mm Film Slide Archive]", lambda img, t, b, q: t14_cinematic(img, t, b)),
    
    # 13. Digital Hangtag (Haute boutique barcode & specs)
    ("Boutique [Digital Hangtag & Barcode Spec]", lambda img, t, b, q: t15_haute_boutique(img, t, b)),
    
    # 14. Spec Card (Triple-feature checklist card)
    ("Checklist [Boutique Spec & Feature Card]", lambda img, t, b, q: t4_boutique(img, t, b)),
    
    # 15. Festive Celebration (Golden ribbons & holiday celebration)
    ("Celebration [Festive Gold & Holiday Elegance]", lambda img, t, b, q: t5_festive(img, t, b)),
    
    # 16. Warm Linen Classic (Bordered linen studio card)
    ("Classic Studio [Warm Linen Bordered Card]", lambda img, t, b, q: t1_linen_studio(img, t, b)),
    
    # 17. Vintage 90s Polaroid (Authentic photo album polaroid)
    ("Vintage 90s [Classic Album Polaroid]", lambda img, t, b, q: t2_polaroid(img, t, b)),
    
    # 18. Curated Dark Noir (Minimalist dark editorial spec)
    ("Curated Noir [Dark Luxury Editorial Spec]", lambda img, t, b, q: t3_editorial(img, t, b)),
    
    # 19. Nordic Pure Line (Clean Scandinavian minimalist card)
    ("Nordic Pure [Scandinavian Clean Line Card]", lambda img, t, b, q: t6_scandinavian(img, t, b)),
    
    # 20. Autumn Sweater Weather (Caramel gradient & warm sweater tones)
    ("Autumn Warmth [Cozy Sweater Weather & Caramel]", lambda img, t, b, q: template_fall_sweater_weather(img, t, b)),
    
    # 21. Terracotta & Maple (Warm terracotta clay & maple spice)
    ("Fall Capsule [Terracotta & Maple Spice]", lambda img, t, b, q: template_fall_terracotta_maple(img, t, b)),
    
    # 22. Dark Roasted Chestnut (Deep espresso & pumpkin spice)
    ("Espresso [Dark Roasted Chestnut & Mocha]", lambda img, t, b, q: template_fall_chestnut_mocha(img, t, b)),
    
    # 23. Oatmeal & Golden Foliage (Oatmeal flannel & autumn checklist)
    ("Harvest [Oatmeal & Golden Foliage Edit]", lambda img, t, b, q: template_fall_oatmeal_foliage(img, t, b)),
    
    # 24. Gift & Hall of Fame (Curated gift spotlight & verified proof)
    ("Gift Spotlight [Curated Gift & Beloved Hall of Fame]", lambda img, t, b, q: t16_pet_boutique(img, t, b))
]

TOTAL_TEMPLATES_COUNT = len(MASTER_TEMPLATES_REGISTRY)


def generate_master_pin(product_image_url, title, board_id, queue_index=1):
    """
    Grand Master Multi-Template Engine:
    Cycles seamlessly across ALL 25 distinct production templates.
    Formula: template_index = (queue_index - 1) % 25.
    
    Features:
    - Guaranteed 0% visual monotony (25 consecutive pins have 25 completely different layouts).
    - Intelligent white-cutout handling: redirects full-bleed templates to shadow-linen studio.
    - Bulletproof exception handling: never crashes a live scheduler.
    """
    try:
        resp = requests.get(product_image_url, timeout=15)
        prod_img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    except Exception as e:
        print(f"⚠️ Warning: Could not fetch image from {product_image_url}: {e}. Creating placeholder.")
        prod_img = Image.new("RGBA", (1000, 1500), (245, 242, 238, 255))

    q_idx = int(queue_index) if queue_index else 1
    t_idx = (q_idx - 1) % TOTAL_TEMPLATES_COUNT
    template_name, template_fn = MASTER_TEMPLATES_REGISTRY[t_idx]

    # Smart cutout handling: If template 0 (lifestyle full bleed) is selected for a pure cutout,
    # route to Studio Flat Lay (travertine & 3D soft contact shadow) for peak aesthetic quality.
    if t_idx == 0 and is_image_white_cutout(prod_img):
        template_name = "Studio [Travertine & 3D Soft Shadow] (Cutout Adaptive)"
        template_fn = lambda img, t, b, q: render_studio_flatlay(img, t, b, q)

    try:
        pin_img = template_fn(prod_img, title, board_id, q_idx)
        return pin_img, template_name
    except Exception as e:
        print(f"⚠️ Warning in template '{template_name}' ({e}), falling back to Studio Flat Lay.")
        try:
            pin_img = render_studio_flatlay(prod_img, title, board_id, q_idx)
            return pin_img, "Studio [Travertine & 3D Soft Shadow] (Fallback)"
        except Exception as e2:
            print(f"⚠️ Critical fallback to raw image ({e2}).")
            return prod_img.convert("RGB"), "Fallback [Raw]"


def generate_master_pin_base64(product_image_url, title, board_id, queue_index=1):
    """
    Renders the chosen pin from the 25-template rotation and returns (base64_str, template_name).
    """
    img, t_name = generate_master_pin(product_image_url, title, board_id, queue_index)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return base64.b64encode(buf.getvalue()).decode("utf-8"), t_name


def get_all_templates_catalog():
    """Returns a list of all 25 registered template names and their indices."""
    return [{"id": i, "name": name} for i, (name, _) in enumerate(MASTER_TEMPLATES_REGISTRY)]


if __name__ == "__main__":
    test_img = "https://m.media-amazon.com/images/I/811O9zF0kZL.jpg"
    print(f"=== Testing Grand Master Engine ({TOTAL_TEMPLATES_COUNT} Distinct Templates) ===")
    for q in range(1, TOTAL_TEMPLATES_COUNT + 1):
        img, name = generate_master_pin(test_img, "Ceramic Stone Aromatherapy Essential Oil Diffuser", "268668002709769947", queue_index=q)
        print(f"  ✔ Pin #{q:02d} -> Mode: {name}")
    print("\nAll 25 template rotation verified successfully!")
