import sys, os
from pathlib import Path
ROOT = Path(os.environ.get("PINTEREST_ROOT", Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "seller_central_store"))

import json
import time
import base64
import argparse
import urllib.parse
from datetime import datetime
from pinterest_api import PinterestAPI
from template_engine_master import generate_master_pin_base64
from clean_apparel_engine import render_masterpiece_pin

USE_BRIDGE = os.environ.get("USE_BRIDGE", "true").lower() == "true"
BRIDGE_BASE_URL = os.environ.get("BRIDGE_BASE_URL", "https://hamouda1.github.io/pinterest-automation/")

# Complete 11 Accounts & Verified Target Board Configuration
ACCOUNTS_CONFIG = [
    {
        "id": "habiboumez",
        "username": "habiboumez",
        "business_name": "Aesthetic Apparel & Lifestyle",
        "queue_file": ROOT / "seller_central_store" / "campaign_queue_habiboumez_60.json",
        "is_seller_apparel": True,
        "default_board_id": "1093037840753522212",
        "default_board_name": "Holiday Season Graphic Sweaters & Gifts"
    },
    {
        "id": "anisds1995",
        "username": "anisds1995",
        "business_name": "CozyNest | Aesthetic Home Decor",
        "queue_file": ROOT / "campaign_queue_anisds.json",
        "is_seller_apparel": False,
        "default_board_id": "1106196795914700327",
        "default_board_name": "Whimsical Christmas & Holiday Home Decor"
    },
    {
        "id": "mhamed1mdaouadji",
        "username": "mhamed1mdaouadji",
        "business_name": "Auraart | Fragrance & Aesthetic Accents",
        "queue_file": ROOT / "campaign_queue_aurascent.json",
        "is_seller_apparel": False,
        "default_board_id": "268668002709769948",
        "default_board_name": "Calming Incense Waterfalls & Rituals"
    },
    {
        "id": "brewaesthetichome",
        "username": "brewaesthetichome",
        "business_name": "BrewAesthetic | Coffee & Matcha Setups",
        "queue_file": ROOT / "campaign_queue_brewaesthetic.json",
        "is_seller_apparel": False,
        "default_board_id": "281615851638486322",
        "default_board_name": "Aesthetic Matcha Rituals & Setups"
    },
    {
        "id": "deskhavenwfh",
        "username": "deskhavenwfh",
        "business_name": "DeskHaven | Workspace & Desk Setup",
        "queue_file": ROOT / "campaign_queue_deskhaven.json",
        "is_seller_apparel": False,
        "default_board_id": "217580294436787518",
        "default_board_name": "Minimalist Desk Setup Inspo"
    },
    {
        "id": "dewyaurabeauty",
        "username": "dewyaurabeauty",
        "business_name": "DewyAura | Korean Skincare Routine",
        "queue_file": ROOT / "campaign_queue_dewyaura.json",
        "is_seller_apparel": False,
        "default_board_id": "254453516385876170",
        "default_board_name": "Viral K-Beauty Sunscreens & Toners"
    },
    {
        "id": "GlowFormWellness",
        "username": "GlowFormWellness",
        "business_name": "GlowForm | Pilates & Fitness Inspo",
        "queue_file": ROOT / "campaign_queue_glowform.json",
        "is_seller_apparel": False,
        "default_board_id": "275071558429949083",
        "default_board_name": "Under-Desk Walking Pads & Active WFH"
    },
    {
        "id": "montessorinest_",
        "username": "montessorinest_",
        "business_name": "MontessoriNest | Baby Nursery & Wooden Toys",
        "queue_file": ROOT / "campaign_queue_montessori.json",
        "is_seller_apparel": False,
        "default_board_id": "1091630465869892618",
        "default_board_name": "Wooden Montessori Toys & Playroom"
    },
    {
        "id": "smallspaceluxe_",
        "username": "smallspaceluxe_",
        "business_name": "SmallSpaceLuxe | Organization Hacks",
        "queue_file": ROOT / "campaign_queue_smallspace.json",
        "is_seller_apparel": False,
        "default_board_id": "266486571640279267",
        "default_board_name": "Under-Sink & Bathroom Storage"
    },
    {
        "id": "luxecanvasco",
        "username": "luxecanvasco",
        "business_name": "LuxeCanvasCo | Aesthetic Templates",
        "queue_file": ROOT / "campaign_queue_luxecanvas.json",
        "is_seller_apparel": False,
        "default_board_id": "267753209035468250",
        "default_board_name": "Canva Presentation Decks & Pitch Decks"
    },
    {
        "id": "marrytreasures",
        "username": "marrytreasures",
        "business_name": "My ArT | Fall & Aesthetic Curations",
        "queue_file": ROOT / "campaign_queue_marrytreasures.json",
        "is_seller_apparel": False,
        "default_board_id": "677440037637741879",
        "default_board_name": "Fruiti Hoodies"
    }
]

def load_accounts_tokens():
    if "PINTEREST_ACCOUNTS_JSON" in os.environ:
        try:
            data = json.loads(os.environ["PINTEREST_ACCOUNTS_JSON"])
            return {k: v.get("access_token") for k, v in data.get("accounts", {}).items()}
        except Exception as e:
            print(f"⚠️ Notice reading PINTEREST_ACCOUNTS_JSON: {e}")
    if (ROOT / "accounts.json").exists():
        with open(ROOT / "accounts.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return {k: v.get("access_token") for k, v in data.get("accounts", {}).items()}
    return {}

def run_network_round(dry_run=False, target_account=None):
    print("=" * 70, flush=True)
    title_suffix = f" [@{target_account}]" if target_account else " (11 ACCOUNTS • EXACT BOARD TARGETING)"
    print(f"🚀 MULTI-ACCOUNT PUBLISHING DISPATCH{title_suffix}", flush=True)
    print("=" * 70, flush=True)
    
    tokens = load_accounts_tokens()
    round_results = []
    
    configs_to_run = [c for c in ACCOUNTS_CONFIG if c["id"] == target_account] if target_account else ACCOUNTS_CONFIG
    
    for cfg in configs_to_run:
        acc_id = cfg["id"]
        b_name = cfg["business_name"]
        q_path = cfg["queue_file"]
        default_bid = cfg["default_board_id"]
        default_bname = cfg["default_board_name"]
        
        print(f"\n👉 Checking Account: @{acc_id} ({b_name})", flush=True)
        token = tokens.get(acc_id)
        if not token:
            print(f"   ❌ No access token found in accounts.json for {acc_id}", flush=True)
            continue
            
        if not q_path.exists():
            print(f"   ❌ Queue file missing: {q_path.name}", flush=True)
            continue
            
        with open(q_path, "r", encoding="utf-8") as f:
            queue = json.load(f)
            
        target_item = None
        target_idx = -1
        for i, item in enumerate(queue):
            if item.get("status") == "pending":
                target_item = item
                target_idx = i
                break
                
        if not target_item:
            print(f"   ℹ️ All pins in queue already published ({len(queue)} total).", flush=True)
            continue
            
        board_id = str(target_item.get("board_id") or default_bid)
        board_name = target_item.get("board_name") or default_bname
        
        title = target_item.get("seo_title") or target_item.get("title") or "Aesthetic Amazon Find"
        raw_link = target_item.get("affiliate_url") or target_item.get("link") or ""
        desc = target_item.get("seo_desc") or target_item.get("description") or title
        
        asin = target_item.get("asin")
        img_url = target_item.get("image_url")
        if USE_BRIDGE and asin and img_url and not cfg.get("is_seller_apparel"):
            params = urllib.parse.urlencode({
                "asin": asin,
                "tag": "mostefa-daoua-20",
                "title": title[:65],
                "img": img_url,
                "tpl": "pin"
            })
            link = f"{BRIDGE_BASE_URL.rstrip('/')}/?{params}"
        else:
            link = raw_link
        
        print(f"   🎯 Target Board: {board_name} (ID: {board_id})", flush=True)
        print(f"   📌 Title: {title[:60]}...", flush=True)
        print(f"   🔗 Link: {link}", flush=True)
        
        if dry_run:
            print("   [DRY RUN] Would publish this pin now.", flush=True)
            round_results.append({
                "account": acc_id,
                "business_name": b_name,
                "board_id": board_id,
                "board_name": board_name,
                "title": title,
                "status": "dry_run_ready"
            })
            continue
            
        api = PinterestAPI(token=token)
        image_base64 = None
        
        if cfg.get("is_seller_apparel"):
            img_file = target_item.get("image_file")
            resolved_img = None
            if img_file and Path(img_file).exists():
                resolved_img = Path(img_file)
            else:
                rel = target_item.get("relative_img") or (Path(img_file).name if img_file else None)
                if rel:
                    cand = ROOT / "seller_central_store" / "batch_queue" / rel
                    if cand.exists():
                        resolved_img = cand
            if resolved_img:
                with open(resolved_img, "rb") as im_f:
                    image_base64 = base64.b64encode(im_f.read()).decode("utf-8")
        else:
            img_url = target_item.get("image_url")
            if img_url:
                try:
                    b64_str, tmpl_name = generate_master_pin_base64(
                        product_image_url=img_url,
                        title=title,
                        board_id=board_id,
                        queue_index=target_item.get("queue_index", target_idx + 1)
                    )
                    image_base64 = b64_str
                    print(f"   🎨 Applied Audited Template: [{tmpl_name}]", flush=True)
                except Exception as e:
                    print(f"   ⚠️ Template notice: {e}, falling back to direct image URL", flush=True)
                    image_base64 = None
                    
        try:
            if image_base64:
                resp = api.create_pin(
                    title=title,
                    description=desc,
                    link=link,
                    board_id=board_id,
                    image_base64=image_base64
                )
            else:
                resp = api.create_pin(
                    title=title,
                    description=desc,
                    link=link,
                    board_id=board_id,
                    image_url=target_item.get("image_url")
                )
                
            pin_id = resp.get("id")
            pin_url = f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else "N/A"
            print(f"   ✅ PUBLISHED! Pin ID: {pin_id} | URL: {pin_url}", flush=True)
            
            target_item["status"] = "published"
            target_item["published"] = True
            target_item["pin_id"] = pin_id
            target_item["pin_url"] = pin_url
            target_item["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(q_path, "w", encoding="utf-8") as f:
                json.dump(queue, f, indent=2, ensure_ascii=False)
                
            round_results.append({
                "account": acc_id,
                "business_name": b_name,
                "board_id": board_id,
                "board_name": board_name,
                "title": title,
                "pin_id": pin_id,
                "pin_url": pin_url,
                "published_at": target_item["published_at"],
                "status": "success"
            })
            
            print("   ⏳ Waiting 5 seconds before next account...", flush=True)
            time.sleep(5)
            
        except Exception as pub_err:
            print(f"   ❌ Failed to publish for @{acc_id}: {pub_err}", flush=True)
            round_results.append({
                "account": acc_id,
                "business_name": b_name,
                "board_id": board_id,
                "board_name": board_name,
                "title": title,
                "error": str(pub_err),
                "status": "failed"
            })
            
    report_file = ROOT / "last_network_publish_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(round_results, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 70, flush=True)
    successful = sum(1 for r in round_results if r.get("status") == "success")
    print(f"🎉 Round Complete: {successful}/{len(ACCOUNTS_CONFIG)} accounts published successfully!", flush=True)
    print(f"📄 Report saved: {report_file}", flush=True)
    print("=" * 70, flush=True)
    return round_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Inspect without publishing")
    parser.add_argument("--account", type=str, default=None, help="Publish only for a specific account ID")
    args = parser.parse_args()
    run_network_round(dry_run=args.dry_run, target_account=args.account)
