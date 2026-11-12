import asyncio
import json
import os
import random
from pathlib import Path
from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"
DATA_FILE = BASE_DIR / "products.json"

SINGLE_TEMPLATES = [
    "template-overlap-en.html",
    "template-arch-editorial.html",
    "template-minimal-ui.html"
]

COLLAGE_TEMPLATES = [
    "template-collage-en.html",
    "template-spotlight-1plus3.html"
]

COLOR_PALETTES = [
    {"bg": "#F4EFEA", "accent": "#B85D3B"},  # Warm Sand & Terracotta
    {"bg": "#EAE3DC", "accent": "#7F4F24"},  # Espresso & Cream
    {"bg": "#EEF1F4", "accent": "#1E293B"},  # Nordic Slate & Ice
    {"bg": "#F1F5F2", "accent": "#2C4A3E"},  # Sage & Forest Green
    {"bg": "#F6F0F4", "accent": "#6D2E46"},  # Dusty Rose & Burgundy
    {"bg": "#F6F4F0", "accent": "#9A3412"}   # Alabaster & Rust
]

def load_template_cache() -> dict:
    """قراءة جميع ملفات HTML في الذاكرة مرة واحدة لرفع السرعة."""
    cache = {}
    for tpl_name in SINGLE_TEMPLATES + COLLAGE_TEMPLATES:
        tpl_path = TEMPLATES_DIR / tpl_name
        if tpl_path.exists():
            cache[tpl_name] = tpl_path.read_text(encoding="utf-8")
        else:
            print(f"[تحذير] الملف غير موجود: {tpl_path}")
    return cache

def render_html(template_str: str, item: dict, palette: dict, is_collage: bool) -> str:
    """استبدال المتغيرات داخل كود HTML."""
    html = template_str.replace("{{BG_COLOR}}", palette["bg"]).replace("{{ACCENT_COLOR}}", palette["accent"])
    html = html.replace("{{CATEGORY}}", item.get("category", "Curated Find"))
    html = html.replace("{{DOMAIN_NAME}}", item.get("domain", ""))

    if is_collage:
        imgs = item.get("images", [])
        html = html.replace("{{COLLECTION_TITLE}}", item.get("title", ""))
        for i in range(4):
            img_url = imgs[i] if i < len(imgs) else (imgs[0] if imgs else "")
            html = html.replace(f"{{{{IMAGE_{i+1}}}}}", img_url)
    else:
        html = html.replace("{{TITLE}}", item.get("title", ""))
        html = html.replace("{{IMAGE_URL}}", item.get("image_url", ""))

    return html

async def process_item(page, item: dict, templates_cache: dict):
    """توليد النسخ المطلوبة لكل منتج أو تجميعة."""
    is_collage = item.get("type") == "collage" or "images" in item
    available_pool = COLLAGE_TEMPLATES if is_collage else SINGLE_TEMPLATES

    valid_templates = [t for t in available_pool if t in templates_cache]
    if not valid_templates:
        print(f"[خطأ] لا توجد قوالب متاحة للعنصر {item.get('id')}")
        return

    variations_count = item.get("variations", 1)

    chosen_templates = random.sample(valid_templates, k=min(variations_count, len(valid_templates)))
    while len(chosen_templates) < variations_count:
        chosen_templates.append(random.choice(valid_templates))

    chosen_palettes = random.sample(COLOR_PALETTES, k=min(variations_count, len(COLOR_PALETTES)))

    for idx in range(variations_count):
        tpl_name = chosen_templates[idx]
        palette = chosen_palettes[idx % len(chosen_palettes)]

        final_html = render_html(templates_cache[tpl_name], item, palette, is_collage)

        await page.set_content(final_html, wait_until="networkidle")

        # التأكد من اكتمال تحميل كافة صور أمازون مع مهلة أمان قصوى
        await page.evaluate("""async () => {
            const selectors = Array.from(document.querySelectorAll("img"));
            await Promise.race([
                Promise.all(selectors.map(img => {
                    if (img.complete) return Promise.resolve();
                    return new Promise((resolve) => {
                        img.addEventListener("load", resolve);
                        img.addEventListener("error", resolve);
                    });
                })),
                new Promise(resolve => setTimeout(resolve, 5000))
            ]);
        }""")

        tpl_short = tpl_name.replace("template-", "").replace(".html", "")
        output_filename = f"{item.get('id', 'pin')}_v{idx+1}_{tpl_short}.jpg"
        output_path = OUTPUT_DIR / output_filename

        await page.screenshot(path=str(output_path), type="jpeg", quality=92)
        print(f"  [تم التوليد] -> {output_filename}")

async def run_generator(data_file_path=None, custom_output_dir=None):
    out_dir = Path(custom_output_dir) if custom_output_dir else OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    templates_cache = load_template_cache()

    data_file = Path(data_file_path) if data_file_path else DATA_FILE
    if not data_file.exists():
        print(f"[خطأ] يرجى إنشاء ملف البيانات {data_file} أولاً.")
        return

    products = json.loads(data_file.read_text(encoding="utf-8"))

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True, channel="msedge")
        except Exception:
            try:
                browser = await p.chromium.launch(headless=True, channel="chrome")
            except Exception:
                browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            viewport={"width": 1000, "height": 1500},
            device_scale_factor=1
        )
        page = await context.new_page()

        print(f"🚀 بدء معالجة {len(products)} عنصر من {data_file.name}...")
        for item in products:
            await process_item(page, item, templates_cache)

        await browser.close()
        print("🎉 اكتملت عملية التوليد الجماعي بنجاح!")

if __name__ == "__main__":
    asyncio.run(run_generator())
