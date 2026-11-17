"""
Apparel Trio Mockup Pinterest Pin Engine
========================================
Builds high-converting 1000x1500 px Pinterest Pins for Amazon Apparel.
Layout Architecture:
- Top Hero (Large, 780px): Authentic model or main product mockup.
- Middle Solid Band (170px): The high-intent search query headline, power badge & Amazon CTA.
- Bottom Split (550px): Two side-by-side secondary lifestyle/flat-lay mockups from Amazon.
- Bulletproof Filter: Programmatically detects and discards blank t-shirt back views.
"""

import os
import sys
import json
import requests
import numpy as np
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT_DIR = Path(r"C:\Users\KIZMO STORE\Documents\pinterest")
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from amazon_api import AmazonSPAPI

W, H = 1000, 1500
FONTS_DIR = ROOT_DIR / "canva_products" / "fonts"
CINZEL_FONT = FONTS_DIR / "Cinzel-Regular.ttf"

# Palettes
PALETTES = {
    "chocolate_brown": {
        "bg": (42, 26, 18),
        "title": (255, 255, 255),
        "eyebrow": (225, 185, 140),
        "gold": (212, 175, 122),
        "sub": (240, 225, 210)
    },
    "midnight_navy": {
        "bg": (20, 32, 52),
        "title": (255, 255, 255),
        "eyebrow": (220, 200, 160),
        "gold": (212, 175, 122),
        "sub": (220, 230, 245)
    },
    "warm_caramel": {
        "bg": (138, 80, 40),
        "title": (255, 255, 255),
        "eyebrow": (255, 240, 215),
        "gold": (245, 215, 165),
        "sub": (250, 235, 220)
    },
    "forest_olive": {
        "bg": (40, 54, 38),
        "title": (255, 255, 255),
        "eyebrow": (215, 230, 205),
        "gold": (212, 175, 122),
        "sub": (230, 240, 225)
    },
    "regal_burgundy": {
        "bg": (68, 18, 28),
        "title": (255, 255, 255),
        "eyebrow": (245, 205, 215),
        "gold": (212, 175, 122),
        "sub": (245, 225, 230)
    },
    "charcoal_slate": {
        "bg": (32, 34, 38),
        "title": (255, 255, 255),
        "eyebrow": (212, 175, 122),
        "gold": (212, 175, 122),
        "sub": (230, 230, 235)
    }
}

CACHE_FILE = ROOT_DIR / "seller_central_store" / "asin_to_clean_image_cache.json"

def update_clean_cache(asin: str, url: str):
    """Saves the clean Amazon product photo URL to the persistent JSON cache."""
    if not asin or not url:
        return
    try:
        cache = {}
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        cache[asin] = url
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"  [Cache Warning] Could not update cache for {asin}: {e}")

def get_cached_clean_image(asin: str) -> str:
    """Reads cached clean Amazon product photo URL for an ASIN if available."""
    if not asin or not CACHE_FILE.exists():
        return ""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
            return cache.get(asin, "")
    except Exception:
        return ""

def is_blank_mockup(im: Image.Image) -> bool:
    """
    Analyzes the center graphic region of the mockup.
    If color variation is low (Std Dev < 35.0), it's a blank t-shirt back view with no graphic.
    Real graphic mockups consistently have Std Dev > 50.0.
    """
    w, h = im.size
    crop = im.crop((int(w * 0.35), int(h * 0.30), int(w * 0.65), int(h * 0.60)))
    arr = np.array(crop.convert("RGB"))
    std = float(np.std(arr))
    return std < 35.0

def fetch_amazon_mockups(asin: str, sp_client: AmazonSPAPI = None):
    """
    Calls SP-API to fetch high-resolution Amazon mockups.
    Filters out any blank back views automatically.
    Also extracts and caches the pristine clean product image URL (MAIN).
    Returns: dict of valid mockup PIL images {variant_name: PIL.Image}
    """
    if sp_client is None:
        sp_client = AmazonSPAPI()
        
    token = sp_client.get_access_token()
    headers = {
        "x-amz-access-token": token,
        "User-Agent": "AntigravityBot/1.0"
    }
    
    cat_url = f"https://sellingpartnerapi-na.amazon.com/catalog/2022-04-01/items/{asin}"
    params = {"marketplaceIds": sp_client.marketplace_id, "includedData": "images,summaries"}
    r = requests.get(cat_url, params=params, headers=headers, timeout=15)
    
    if r.status_code != 200:
        raise RuntimeError(f"SP-API returned {r.status_code} for ASIN {asin}: {r.text}")
        
    data = r.json()
    valid_mockups = {}
    clean_product_url = None
    
    # First pass: find the clean MAIN product image for landing page
    for iset in data.get("images", []):
        for im_meta in iset.get("images", []):
            v = im_meta.get("variant")
            h = im_meta.get("height", 0)
            link = im_meta.get("link", "")
            if v == "MAIN" and h and h >= 1000 and "SL75" not in link and not clean_product_url:
                clean_product_url = link
                break
        if clean_product_url:
            break
            
    if clean_product_url:
        update_clean_cache(asin, clean_product_url)
    
    for iset in data.get("images", []):
        for im_meta in iset.get("images", []):
            v = im_meta.get("variant")
            h = im_meta.get("height", 0)
            link = im_meta.get("link", "")
            
            # Target full resolution only
            if h and h >= 1000 and "SL75" not in link and v not in valid_mockups:
                # Download and inspect
                try:
                    resp = requests.get(link, timeout=12)
                    if resp.status_code == 200:
                        im = Image.open(BytesIO(resp.content)).convert("RGB")
                        
                        # Apply Blank Detector
                        if is_blank_mockup(im):
                            print(f"  [Filter] Skipped blank back view for {asin} (variant: {v})")
                            continue
                        
                        valid_mockups[v] = im
                except Exception as e:
                    print(f"  [Warning] Failed to fetch image {link}: {e}")
                    
    # Store clean_product_url as special attribute if found
    if clean_product_url:
        valid_mockups["__clean_product_url__"] = clean_product_url
        
    return valid_mockups

def select_trio_images(mockups: dict):
    """
    Selects 3 distinct images:
    1. Hero: Model (PT01) > MAIN
    2. Sub Left: Folded (PT03) > Next available
    3. Sub Right: Chair/Lifestyle (PT04) > Next available
    """
    # Only keep PIL Image objects
    img_mockups = {k: v for k, v in mockups.items() if isinstance(v, Image.Image)}
    if not img_mockups:
        raise ValueError("No valid image objects found in mockups.")

    # 1. Hero
    if "PT01" in img_mockups:
        hero = img_mockups["PT01"]
        remaining = [v for v in img_mockups if v != "PT01"]
    elif "MAIN" in img_mockups:
        hero = img_mockups["MAIN"]
        remaining = [v for v in img_mockups if v != "MAIN"]
    else:
        k = list(img_mockups.keys())[0]
        hero = img_mockups[k]
        remaining = [v for v in img_mockups if v != k]
        
    # 2. Sub1
    sub1_key = None
    for target in ["PT03", "MAIN", "PT04", "PT02", "PT05"]:
        if target in remaining:
            sub1_key = target
            break
    if not sub1_key and remaining:
        sub1_key = remaining[0]
        
    sub1 = img_mockups[sub1_key] if sub1_key else hero
    if sub1_key:
        remaining.remove(sub1_key)
        
    # 3. Sub2
    sub2_key = None
    for target in ["PT04", "PT03", "MAIN", "PT05", "PT06"]:
        if target in remaining:
            sub2_key = target
            break
    if not sub2_key and remaining:
        sub2_key = remaining[0]
        
    sub2 = img_mockups[sub2_key] if sub2_key else (img_mockups["MAIN"] if "MAIN" in img_mockups else hero)
    
    return hero, sub1, sub2

def render_apparel_trio_pin(
    asin: str,
    search_title: str,
    eyebrow: str = "OFFICIAL AMAZON EXCLUSIVE • BEST SELLER",
    palette_name: str = "chocolate_brown",
    output_path: str = None,
    sp_client: AmazonSPAPI = None,
    return_clean_url: bool = False
):
    """
    Main entry point: fetches images, applies blank filter, and renders the 1000x1500 trio pin.
    """
    p = PALETTES.get(palette_name, PALETTES["chocolate_brown"])
    mockups = fetch_amazon_mockups(asin, sp_client)
    clean_url = mockups.get("__clean_product_url__") or get_cached_clean_image(asin)
    
    if not mockups:
        raise ValueError(f"No valid mockups found for ASIN {asin}")
        
    hero_im, sub1_im, sub2_im = select_trio_images(mockups)
    
    # Canvas
    pin = Image.new("RGB", (W, H), (248, 246, 242))
    
    # 1. Top Section (Large Hero Image - 780px)
    top_h = 780
    top_fitted = ImageOps.fit(hero_im, (W, top_h), centering=(0.5, 0.35))
    pin.paste(top_fitted, (0, 0))
    
    # 2. Middle Section (Solid Text Banner - 170px)
    band_y = top_h
    band_h = 170
    band = Image.new("RGB", (W, band_h), p["bg"])
    bdraw = ImageDraw.Draw(band)
    
    # Gold Hairlines
    bdraw.line([0, 0, W, 0], fill=p["gold"], width=2)
    bdraw.line([0, band_h - 1, W, band_h - 1], fill=p["gold"], width=2)
    
    # Fonts
    try:
        font_eye = ImageFont.truetype("arialbd.ttf", 15)
        # Font size scaling based on length
        title_len = len(search_title)
        if title_len > 32:
            font_title = ImageFont.truetype(str(CINZEL_FONT), 33)
        elif title_len > 24:
            font_title = ImageFont.truetype(str(CINZEL_FONT), 37)
        else:
            font_title = ImageFont.truetype(str(CINZEL_FONT), 41)
        font_cta = ImageFont.truetype("arialbd.ttf", 15)
    except:
        font_eye = font_title = font_cta = ImageFont.load_default()
        
    bdraw.text((W // 2, 38), eyebrow.upper(), font=font_eye, fill=p["eyebrow"], anchor="mm")
    bdraw.text((W // 2, 90), search_title.upper(), font=font_title, fill=p["title"], anchor="mm")
    bdraw.text((W // 2, 138), "DISCOVER ON AMAZON  >", font=font_cta, fill=p["gold"], anchor="mm")
    
    pin.paste(band, (0, band_y))
    
    # 3. Bottom Section (Two Side-by-Side Smaller Mockups - 550px)
    bot_y = band_y + band_h
    bot_h = H - bot_y
    margin = 15
    gap = 12
    img_w = (W - (2 * margin) - gap) // 2
    img_h = bot_h - (2 * margin)
    
    left_fitted = ImageOps.fit(sub1_im, (img_w, img_h), centering=(0.5, 0.45))
    right_fitted = ImageOps.fit(sub2_im, (img_w, img_h), centering=(0.5, 0.45))
    
    ImageDraw.Draw(left_fitted).rectangle([0, 0, img_w - 1, img_h - 1], outline=(220, 210, 200), width=2)
    ImageDraw.Draw(right_fitted).rectangle([0, 0, img_w - 1, img_h - 1], outline=(220, 210, 200), width=2)
    
    pin.paste(left_fitted, (margin, bot_y + margin))
    pin.paste(right_fitted, (margin + img_w + gap, bot_y + margin))
    
    # Outer 1px frame
    ImageDraw.Draw(pin).rectangle([0, 0, W - 1, H - 1], outline=(200, 185, 170), width=1)
    
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        pin.save(output_path, "JPEG", quality=95)
        print(f"✔ Successfully saved Trio Pin to: {output_path}")
        
    if return_clean_url:
        return pin, clean_url
    return pin

if __name__ == "__main__":
    print("Apparel Trio Engine Loaded.")
