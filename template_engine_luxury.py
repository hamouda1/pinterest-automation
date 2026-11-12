import sys
import io
import base64
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

FONTS_DIR_CANDIDATE = Path(__file__).resolve().parent / "fonts"
FONT_DIR = str(FONTS_DIR_CANDIDATE) if FONTS_DIR_CANDIDATE.exists() else r"C:\Windows\Fonts"
FONT_TITLE_SERIF = ImageFont.truetype(rf"{FONT_DIR}\georgiab.ttf", 36)
FONT_TITLE_LARGE = ImageFont.truetype(rf"{FONT_DIR}\georgiab.ttf", 42)
FONT_SUB_SERIF = ImageFont.truetype(rf"{FONT_DIR}\georgia.ttf", 20)
FONT_SUB_ITALIC = ImageFont.truetype(rf"{FONT_DIR}\georgia.ttf", 19)
FONT_SANS_BOLD = ImageFont.truetype(rf"{FONT_DIR}\segoeuib.ttf", 21)
FONT_SANS_MED = ImageFont.truetype(rf"{FONT_DIR}\segoeuib.ttf", 15)
FONT_SANS_SMALL = ImageFont.truetype(rf"{FONT_DIR}\segoeuib.ttf", 13)
FONT_SANS_REG = ImageFont.truetype(rf"{FONT_DIR}\segoeui.ttf", 15)
FONT_STARS = ImageFont.truetype(rf"{FONT_DIR}\segoeui.ttf", 22)
FONT_QUOTE_BIG = ImageFont.truetype(rf"{FONT_DIR}\georgiab.ttf", 64)

# -------------------------------------------------------------
# Text Wrapping Helper (Guarantees 0% text overflow anywhere)
# -------------------------------------------------------------
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

# Context-Aware Copy Database (All 5 Active Accounts & 31 Strategic Boards)
BOARD_COPY = {
    # Account 1: @habiboumez (Streetwear & Apparel)
    "1093037840753522205": {
        "board_name": "Trending Graphic Tees",
        "badge": "TRENDING GRAPHIC APPAREL",
        "sub": "Relaxed Y2K Casual Style • Easy Daily Layering",
        "quote": "“The fit is effortlessly flattering and the fabric is incredibly soft. Gets compliments every single time!”",
        "btn_color": (195, 75, 55, 255),
        "btn_text": "CHECK CURRENT PRICE ON AMAZON ↗",
        "formula_label": "OUTFIT STYLING FORMULA:",
        "formula": "• Pair with wide-leg denim or cargos  • Layer with an oversized blazer or trench  • Finish with clean retro sneakers"
    },
    "1093037840753522206": {
        "board_name": "Cozy Hoodies & Streetwear",
        "badge": "COZY STREETWEAR HOODIE",
        "sub": "Plush Fleece Lining • Relaxed Drop-Shoulder Fit",
        "quote": "“Literally the comfiest hoodie I own. Thick, warm, and holds up perfectly after multiple washes.”",
        "btn_color": (45, 55, 72, 255),
        "btn_text": "CHECK SIZES & REVIEWS ON AMAZON ↗",
        "formula_label": "OUTFIT STYLING FORMULA:",
        "formula": "• Layer over a vintage graphic tee  • Pair with relaxed joggers or baggy denim  • Style with high-top kicks & tote bag"
    },
    "1093037840753522208": {
        "board_name": "Cute Pet Lover Shirts & Gifts",
        "badge": "CUTE PET LOVER GIFT",
        "sub": "Adorable Pet Illustration • All-Day Soft Comfort",
        "quote": "“Bought this for my sister who is a huge cat lover. She absolutely adored it—soft and true to size!”",
        "btn_color": (180, 85, 20, 255),
        "btn_text": "CHECK AVAILABILITY ON AMAZON ↗",
        "formula_label": "GIFT & STYLING FORMULA:",
        "formula": "• Style with casual weekend shorts or denim  • Perfect cozy gift for cat & dog parents  • Pair with a warm knit cardigan"
    },
    "1093037840753522209": {
        "board_name": "Viral Amazon Fashion",
        "badge": "VIRAL AMAZON FASHION FIND",
        "sub": "Chic & Flattering Silhouette • Wardrobe Staple",
        "quote": "“Saw this trending everywhere and had to try it. Worth every penny—flattering, chic, and comfortable.”",
        "btn_color": (195, 75, 55, 255),
        "btn_text": "CHECK CURRENT PRICE ON AMAZON ↗",
        "formula_label": "CAPSULE STYLING FORMULA:",
        "formula": "• Essential capsule wardrobe silhouette  • Transition effortlessly from casual day to night  • Style with gold accent jewelry"
    },
    "1093037840753522211": {
        "board_name": "Vintage Retro Tees & 90s Fits",
        "badge": "VINTAGE 90s RETRO TEE",
        "sub": "Authentic Retro Aesthetic • Timeless Faded Wash",
        "quote": "“Has that genuine vintage band tee feel. Soft, durable cotton with an authentic 90s indie drape.”",
        "btn_color": (120, 65, 30, 255),
        "btn_text": "EXPLORE RETRO FIT ON AMAZON ↗",
        "formula_label": "90s RETRO FORMULA:",
        "formula": "• Tuck into high-waisted vintage jeans  • Layer under a distressed leather jacket  • Complete the 90s grunge look with boots"
    },
    "1093037840753522212": {
        "board_name": "Holiday Season Graphic Sweaters",
        "badge": "HOLIDAY GRAPHIC SWEATER",
        "sub": "Cozy Festive Pullover • Perfect for Holiday Gatherings",
        "quote": "“The cutest holiday sweater! Not scratchy at all, super cozy, and made everyone smile at our party.”",
        "btn_color": (160, 30, 30, 255),
        "btn_text": "CHECK HOLIDAY AVAILABILITY ON AMAZON ↗",
        "formula_label": "FESTIVE STYLING FORMULA:",
        "formula": "• Perfect for festive parties & holiday photos  • Pair with cozy cords or pleated winter skirts  • Keeps you toasty warm all evening"
    },

    # Account 2: @marrytreasures (Graphic Tees & Novelty Gifts)
    "677440037639174208": {
        "board_name": "Cozy Fall & Thanksgiving Finds",
        "badge": "COZY FALL & THANKSGIVING",
        "sub": "Warm Harvest Palette • Autumn Gathering Essential",
        "quote": "“Beautiful fall colors and exceptional quality. Perfect for Thanksgiving dinner and crisp autumn days.”",
        "btn_color": (175, 80, 35, 255),
        "btn_text": "CHECK FALL AVAILABILITY ON AMAZON ↗",
        "formula_label": "AUTUMN HARVEST FORMULA:",
        "formula": "• Pair with warm caramel knits and boots  • Ideal for Thanksgiving family dinners  • Brings cozy autumn vibes everywhere"
    },
    "677440037639168259": {
        "board_name": "Thanksgiving Celebrations",
        "badge": "THANKSGIVING CELEBRATION",
        "sub": "Festive Holiday Gathering • Warm Autumn Tone",
        "quote": "“Everyone at Thanksgiving dinner asked where I got this! Super charming and comfortable.”",
        "btn_color": (185, 70, 25, 255),
        "btn_text": "ORDER FOR THANKSGIVING ON AMAZON ↗",
        "formula_label": "THANKSGIVING STYLING:",
        "formula": "• Style with warm earth tones and boots  • Perfect festive statement piece for autumn  • Comfortable for all-day family celebrations"
    },
    "677440037639070616": {
        "board_name": "Trending Graphic Apparel",
        "badge": "TRENDING GRAPHIC APPAREL",
        "sub": "Original Aesthetic Graphic • Everyday Casual",
        "quote": "“Great print quality that doesn't fade. Love the relaxed cut and breathable cotton fabric.”",
        "btn_color": (195, 75, 55, 255),
        "btn_text": "EXPLORE SIZES ON AMAZON ↗",
        "formula_label": "DAILY CASUAL FORMULA:",
        "formula": "• Pair with denim shorts or relaxed jeans  • Layer under an oversized flannel shirt  • Clean casual look for everyday wear"
    },
    "677440037639070445": {
        "board_name": "Funny Cat Lover Gifts & Shirts",
        "badge": "FUNNY CAT LOVER GIFT",
        "sub": "Clever Whimsical Design • Delightful Pet Gift",
        "quote": "“Hilarious and incredibly soft! Ordered for a cat owner friend and they laughed out loud. 10/10 gift!”",
        "btn_color": (180, 95, 25, 255),
        "btn_text": "CHECK GIFT AVAILABILITY ON AMAZON ↗",
        "formula_label": "PET LOVER GIFT FORMULA:",
        "formula": "• Delightful gift for cat moms and dads  • High-comfort loungewear for casual days  • Guaranteed to bring smiles and compliments"
    },
    "677440037639166201": {
        "board_name": "Cozy Graphic Hoodies",
        "badge": "COZY GRAPHIC HOODIE",
        "sub": "Playful Aesthetic Design • Warm Fleece Lining",
        "quote": "“Super cute design, plush fabric, and keeps you warm without feeling heavy. Highly recommended!”",
        "btn_color": (50, 60, 75, 255),
        "btn_text": "CHECK COLORS ON AMAZON ↗",
        "formula_label": "COZY HOODIE FORMULA:",
        "formula": "• Layer over everyday t-shirts  • Pair with leggings or relaxed streetwear pants  • Your go-to comfort layer for cool days"
    },
    "677440037639128972": {
        "board_name": "Goblincore & Cottagecore Finds",
        "badge": "GOBLINCORE & COTTAGECORE",
        "sub": "Earthy Woodland Aesthetics • Whimsical Nature Vibe",
        "quote": "“Has that magical earthy feel I was looking for. Sturdy quality, lovely colors, and very comfortable.”",
        "btn_color": (75, 95, 60, 255),
        "btn_text": "DISCOVER COTTAGECORE ON AMAZON ↗",
        "formula_label": "WOODLAND AESTHETIC FORMULA:",
        "formula": "• Pair with forest green or brown corduroy  • Layer with chunky knit cardigans  • Earthy nature aesthetic for free spirits"
    },
    "677440037639094964": {
        "board_name": "Funny Sarcastic Novelty Gifts",
        "badge": "SARCASTIC NOVELTY HUMOR",
        "sub": "Witty Statement Graphic • Great Gift Conversation Starter",
        "quote": "“Got this as a gag gift and it turned out to be their favorite shirt. High quality print and super funny!”",
        "btn_color": (145, 65, 85, 255),
        "btn_text": "CHECK SIZES & HUMOR ON AMAZON ↗",
        "formula_label": "STATEMENT PIECE FORMULA:",
        "formula": "• Wear to casual gatherings & weekend hangouts  • The perfect gift for the friend with great humor  • Pair with simple jeans for full focus on the joke"
    },

    # Account 3: @anisds1995 (Cozy Home & Holiday Decor)
    "1106196795914700326": {
        "board_name": "Cozy Living Room & Warm Lighting",
        "badge": "COZY LIVING ROOM ACCENT",
        "sub": "Warm Ambient Living • Relaxed Evening Aesthetic",
        "quote": "“Transformed our living room instantly! The glow and texture create such an inviting, cozy atmosphere.”",
        "btn_color": (160, 95, 45, 255),
        "btn_text": "CHECK LIVING ROOM ACCENT ON AMAZON ↗",
        "formula_label": "LIVING ROOM ACCENT FORMULA:",
        "formula": "• Place beside warm ambient floor lamps  • Style with chunky knit throws on the sofa  • Creates a serene, welcoming living space"
    },
    "1106196795914700327": {
        "board_name": "Whimsical Christmas & Holiday Decor",
        "badge": "WHIMSICAL HOLIDAY DECOR",
        "sub": "Festive Holiday Magic • Charming Seasonal Accents",
        "quote": "“The cutest Christmas decoration in our home! Beautiful details that bring instant holiday warmth.”",
        "btn_color": (155, 35, 35, 255),
        "btn_text": "EXPLORE HOLIDAY DECOR ON AMAZON ↗",
        "formula_label": "FESTIVE HOLIDAY FORMULA:",
        "formula": "• Display on fireplace mantel or entryway console  • Combine with warm fairy lights and pine garlands  • Creates magical holiday memories for guests"
    },
    "1106196795914700328": {
        "board_name": "Aesthetic Bedroom & Chunky Throws",
        "badge": "COZY BEDROOM SANCTUARY",
        "sub": "Plush Textures & Serene Tones • Restful Aesthetic",
        "quote": "“Incredibly soft and looks like a boutique luxury hotel bed. Makes sleeping so much cozier!”",
        "btn_color": (140, 110, 85, 255),
        "btn_text": "VIEW BEDROOM ESSENTIAL ON AMAZON ↗",
        "formula_label": "BEDROOM SANCTUARY FORMULA:",
        "formula": "• Layer over crisp white or linen bedding  • Complement with warm bedside lamps and ceramic vases  • Enhances peaceful, restorative rest"
    },
    "1106196795914700329": {
        "board_name": "Holiday Dining & Table Setting",
        "badge": "ELEGANT DINING & TABLESCAPE",
        "sub": "Sophisticated Entertaining • Warm Dinner Accents",
        "quote": "“Made our dinner table look like a magazine spread. Guests were truly impressed by the elegance!”",
        "btn_color": (135, 75, 45, 255),
        "btn_text": "VIEW TABLE SETTING ON AMAZON ↗",
        "formula_label": "TABLESCAPE ENTERTAINING FORMULA:",
        "formula": "• Center on a neutral linen table runner  • Pair with taper candles and ceramic tableware  • Sets an unforgettable dinner ambience"
    },
    "1106196795914700330": {
        "board_name": "Cozy Coffee Bar & Kitchen Aesthetic",
        "badge": "COZY COFFEE BAR EDIT",
        "sub": "Artisan Kitchen Details • Morning Ritual Aesthetic",
        "quote": "“Upgraded my morning coffee routine completely! High quality finish and looks stunning on the counter.”",
        "btn_color": (120, 80, 50, 255),
        "btn_text": "EXPLORE KITCHEN ACCENT ON AMAZON ↗",
        "formula_label": "COFFEE STATION FORMULA:",
        "formula": "• Arrange neatly on an espresso or coffee station  • Pair with amber syrup bottles and ribbed mugs  • Turns every morning into a cafe experience"
    },
    "1106196795914700331": {
        "board_name": "Aesthetic Candles & Scented Home",
        "badge": "AESTHETIC HOME CANDLE",
        "sub": "Warm Ambient Glow • Subtle Calming Fragrance",
        "quote": "“Burns evenly, smells divine without being overpowering, and looks like a designer decor piece!”",
        "btn_color": (175, 115, 45, 255),
        "btn_text": "CHECK CANDLE ACCENT ON AMAZON ↗",
        "formula_label": "WARM AMBIENCE FORMULA:",
        "formula": "• Place on a travertine or marble coaster  • Light during evening wind-down rituals  • Fills the room with a serene, luxurious aroma"
    },

    # Account 4: @deskhavenwfh (Minimalist Workspace & Desk Setup)
    "217580294436787518": {
        "board_name": "Minimalist Desk Setup Inspo",
        "badge": "MINIMALIST DESK SETUP",
        "sub": "Clean Workspace Architecture • Focused Productivity",
        "quote": "“Completely eliminated clutter from my desk. Clean, sleek, and makes working from home a pure joy.”",
        "btn_color": (40, 50, 60, 255),
        "btn_text": "VIEW DESK ESSENTIAL ON AMAZON ↗",
        "formula_label": "MINIMALIST WORKSPACE FORMULA:",
        "formula": "• Center on an oversized wool felt desk mat  • Pair with a wireless low-profile keyboard & mouse  • Keeps your workspace clean, minimal, and focused"
    },
    "217580294436787519": {
        "board_name": "Cozy WFH & Study Spaces",
        "badge": "COZY WFH WORKSPACE",
        "sub": "Comfortable Ergonomics • Calm Work Sanctuary",
        "quote": "“Game changer for long working hours! Superior comfort and looks gorgeous in my home office.”",
        "btn_color": (65, 75, 85, 255),
        "btn_text": "CHECK WFH UPGRADE ON AMAZON ↗",
        "formula_label": "ERGONOMIC COMFORT FORMULA:",
        "formula": "• Position for natural window lighting  • Add an ergonomic wrist rest and desk plant  • Designed for all-day focus without fatigue"
    },
    "217580294436787520": {
        "board_name": "Aesthetic Tech & Accessories",
        "badge": "AESTHETIC TECH ACCESSORY",
        "sub": "Modern Tech Design • Seamless Workspace Workflow",
        "quote": "“Super premium build quality! Blends right into my minimalist tech aesthetic and works flawlessly.”",
        "btn_color": (35, 45, 55, 255),
        "btn_text": "EXPLORE TECH FIND ON AMAZON ↗",
        "formula_label": "SEAMLESS TECH FORMULA:",
        "formula": "• Connect seamlessly with modern USB-C setups  • Compliments aluminum laptops and monitor stands  • Combines peak utility with modern aesthetics"
    },
    "217580294436787521": {
        "board_name": "Desk Org & Cable Management",
        "badge": "DESK ORGANIZATION ESSENTIAL",
        "sub": "Zero-Clutter Philosophy • Precision Workspace Order",
        "quote": "“Finally hidden all the ugly tangled wires! My desk looks 10x bigger, cleaner, and more professional.”",
        "btn_color": (55, 65, 75, 255),
        "btn_text": "CHECK DESK ORGANIZER ON AMAZON ↗",
        "formula_label": "CABLE MANAGEMENT FORMULA:",
        "formula": "• Mount securely under desk or behind monitor  • Route power cables neatly into single clean trunk  • Immediate visual tranquility and zero clutter"
    },
    "217580294436787522": {
        "board_name": "Warm Ambient Desk Lighting",
        "badge": "WARM DESK AMBIENT LIGHTING",
        "sub": "Glare-Free Illumination • Evening Flow State",
        "quote": "“The warm 2700K light is gentle on the eyes during late night coding sessions. Absolutely love it!”",
        "btn_color": (195, 125, 40, 255),
        "btn_text": "VIEW AMBIENT LIGHT ON AMAZON ↗",
        "formula_label": "EVENING FLOW STATE FORMULA:",
        "formula": "• Place behind monitor for indirect ambient glow  • Adjust brightness for relaxed evening focus  • Reduces eye strain and creates a cozy glow"
    },
    "217580294436787523": {
        "board_name": "Viral Amazon Workspace Finds",
        "badge": "VIRAL AMAZON WORKSPACE PICK",
        "sub": "High-Utility WFH Innovation • Top Verified Rating",
        "quote": "“Saw this on TikTok and had to get it. One of the best purchases I've ever made for my desk setup!”",
        "btn_color": (45, 55, 65, 255),
        "btn_text": "CHECK CURRENT PRICE ON AMAZON ↗",
        "formula_label": "WORKSPACE ESSENTIAL FORMULA:",
        "formula": "• Integrates effortlessly into any desk style  • Elevates daily productivity and aesthetic appeal  • High rating backed by thousands of WFH reviews"
    },

    # Account 5: @mhamed1mdaouadji (Aura Scent - Ritualistic Fragrance)
    "268668002709769945": {
        "board_name": "Scent Stacking & Layering",
        "badge": "SCENT STACKING RITUAL",
        "sub": "Artisan Fragrance Layering • Signature Home Scent",
        "quote": "“Layering these scents transformed our home. Guests constantly ask what smells so amazingly luxurious!”",
        "btn_color": (165, 95, 45, 255),
        "btn_text": "EXPLORE SCENT LAYERING ON AMAZON ↗",
        "formula_label": "SCENT STACKING RITUAL FORMULA:",
        "formula": "• Start with an amber reed diffuser as subtle base  • Light a woody soy candle 30 minutes before guests  • Mist linen spray on curtains for lasting depth"
    },
    "268668002709769946": {
        "board_name": "Candle Warmers & Amber Glass",
        "badge": "FLAMELESS CANDLE WARMER",
        "sub": "Safe Halogen Melting • Long-Lasting Pure Fragrance",
        "quote": "“No open flames, candles last 3x longer, and the amber glow creates the dreamiest evening ambiance!”",
        "btn_color": (180, 110, 40, 255),
        "btn_text": "VIEW CANDLE WARMER ON AMAZON ↗",
        "formula_label": "CANDLE WARMER RITUAL FORMULA:",
        "formula": "• Place your favorite jar candle under top-down lamp  • Adjust timer & dimmer for perfect evening scent release  • Safer around pets and leaves zero soot"
    },
    "268668002709769947": {
        "board_name": "Ceramic Stone Diffusers & Oils",
        "badge": "CERAMIC STONE DIFFUSER",
        "sub": "Ultrasonic Cold Diffusion • Natural Essential Oils",
        "quote": "“Looks like a high-end sculpture from a luxury spa! Whisper quiet and fills my living room with peace.”",
        "btn_color": (145, 105, 75, 255),
        "btn_text": "CHECK STONE DIFFUSER ON AMAZON ↗",
        "formula_label": "ULTRASONIC DIFFUSION FORMULA:",
        "formula": "• Add 6-8 drops of lavender, cedarwood, or bergamot  • Position on a stone coaster in living room or bedroom  • Enjoy calming, continuous ultrasonic mist"
    },
    "268668002709769948": {
        "board_name": "Calming Incense Waterfalls",
        "badge": "RITUALISTIC INCENSE WATERFALL",
        "sub": "Hypnotic Backflow Smoke • Mindful Meditation Ritual",
        "quote": "“Mesmerizing smoke waterfall effect! Truly calming after a stressful workday. A meditation essential.”",
        "btn_color": (80, 55, 65, 255),
        "btn_text": "DISCOVER INCENSE RITUAL ON AMAZON ↗",
        "formula_label": "MINDFUL MEDITATION FORMULA:",
        "formula": "• Place backflow cone atop ceramic waterfall burner  • Light cone and watch thick smoke cascade like silk  • Use during meditation, yoga, or reading hours"
    },
    "268668002709769949": {
        "board_name": "Luxury Linen Mists & Sprays",
        "badge": "LUXURY ROOM & LINEN MIST",
        "sub": "Fine Botanical Botanicals • Instant Atmosphere Refresh",
        "quote": "“Spritzed on my pillows and fresh sheets. It feels like slipping into a 5-star boutique hotel bed every night!”",
        "btn_color": (115, 125, 95, 255),
        "btn_text": "SHOP LINEN MIST ON AMAZON ↗",
        "formula_label": "LINEN MIST APPLICATION FORMULA:",
        "formula": "• Spray 2-3 mists over fresh bedding and curtains  • Keep by entryway for a welcoming burst of aroma  • Plant-based, alcohol-free gentle botanicals"
    },
    "268668002709769950": {
        "board_name": "Viral Amazon Home Scent",
        "badge": "VIRAL HOME SCENT FAVORITE",
        "sub": "Pinterest Predicts 2026 Breakout • Self-Care Ritual",
        "quote": "“Ranked #1 for a reason. Luxurious presentation, divine aroma, and incredible value for money!”",
        "btn_color": (170, 95, 45, 255),
        "btn_text": "CHECK CURRENT PRICE ON AMAZON ↗",
        "formula_label": "SELF-CARE RITUAL FORMULA:",
        "formula": "• The ultimate ritual gift for yourself or loved ones  • Blends effortlessly into modern organic interiors  • Top verified customer reviews and fast shipping"
    }
}

DEFAULT_C = {
    "board_name": "Aesthetic Lifestyle",
    "badge": "VIRAL AMAZON FIND",
    "sub": "Curated Aesthetic Lifestyle Favorite",
    "quote": "“High quality, comfortable everyday staple with top verified customer ratings on Amazon.”",
    "btn_color": (195, 75, 55, 255),
    "btn_text": "TAP TO VIEW ON AMAZON ↗"
}

def draw_luxury_button(base, draw, y, text, fill, W=1000):
    btn_w, btn_h = 520, 68
    bx = (W - btn_w) // 2
    
    # Soft button glow/shadow
    b_shadow = Image.new("RGBA", (btn_w + 30, btn_h + 30), (0, 0, 0, 0))
    ImageDraw.Draw(b_shadow).rounded_rectangle([15, 15 + 4, 15 + btn_w, 15 + btn_h + 4], radius=34, fill=(0, 0, 0, 40))
    base.alpha_composite(b_shadow.filter(ImageFilter.GaussianBlur(8)), (bx - 15, y - 15))
    
    draw.rounded_rectangle([bx, y, bx + btn_w, y + btn_h], radius=34, fill=fill)
    c_bb = FONT_SANS_BOLD.getbbox(text)
    tw = c_bb[2] - c_bb[0]
    draw.text((bx + (btn_w - tw)//2, y + 20), text, font=FONT_SANS_BOLD, fill=(255, 255, 255, 255))

def draw_ftc(draw, y, W=1000, color=(140, 135, 125, 255)):
    ftc = "As an Amazon Associate I earn from qualifying purchases • #ad"
    bb = FONT_SANS_REG.getbbox(ftc)
    draw.text(((W - (bb[2]-bb[0]))//2, y), ftc, font=FONT_SANS_REG, fill=color)

# -------------------------------------------------------------
# 16 REFINED LUXURY TEMPLATES
# -------------------------------------------------------------

# 1. Warm Linen Studio
def t1_linen_studio(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (252, 250, 246, 255))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([35, 35, W - 35, H - 35], radius=20, outline=(225, 218, 205, 255), width=2)
    
    # Minimalist Badge
    b_bb = FONT_SANS_SMALL.getbbox(c["badge"])
    bw = b_bb[2] - b_bb[0] + 36
    draw.rounded_rectangle([(W - bw)//2, 65, (W + bw)//2, 98], radius=16, fill=(35, 40, 45, 255))
    draw.text(((W - (b_bb[2]-b_bb[0]))//2, 72), c["badge"], font=FONT_SANS_SMALL, fill=(255, 255, 255, 255))
    
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (28, 28, 30, 255), 840, 80, 115)
    draw_safe_text(draw, c["sub"], FONT_SUB_SERIF, (120, 112, 102, 255), 840, 80, 168)
    
    card_w, card_h = 820, 860
    cx, cy = (W - card_w)//2, 225
    shadow = Image.new("RGBA", (card_w + 50, card_h + 50), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([25, 30, 25 + card_w, 30 + card_h], radius=26, fill=(0, 0, 0, 40))
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(16)), (cx - 25, cy - 25))
    
    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    c_draw = ImageDraw.Draw(card)
    c_draw.rounded_rectangle([0, 0, card_w, card_h], radius=24, outline=(238, 234, 226, 255), width=2)
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))
    
    draw.text((cx + 170, 1125), "★★★★★", font=FONT_STARS, fill=(245, 166, 35, 255))
    draw.text((cx + 295, 1128), "Verified Customer Favorite", font=FONT_SANS_MED, fill=(70, 65, 58, 255))
    draw_luxury_button(base, draw, 1185, c["btn_text"], c["btn_color"])
    draw_ftc(draw, 1275)
    return base.convert("RGB")

# 2. Vintage 90s Polaroid (Clean, no tacky tape)
def t2_polaroid(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (238, 233, 222, 255))
    draw = ImageDraw.Draw(base)
    
    draw_safe_text(draw, f"• {c['badge']} •", FONT_SANS_MED, (80, 75, 65, 255), 840, 80, 55)
    draw_safe_text(draw, c["sub"], FONT_SUB_SERIF, (120, 112, 98, 255), 840, 80, 90)
    
    pol_w, pol_h = 820, 970
    px, py = (W - pol_w)//2, 140
    shadow = Image.new("RGBA", (pol_w + 40, pol_h + 40), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle([20, 24, 20 + pol_w, 24 + pol_h], fill=(0, 0, 0, 45))
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)), (px - 20, py - 20))
    
    pol = Image.new("RGBA", (pol_w, pol_h), (255, 254, 250, 255))
    p_draw = ImageDraw.Draw(pol)
    p_draw.rectangle([0, 0, pol_w, pol_h], outline=(225, 220, 208, 255), width=2)
    
    photo_w, photo_h = 740, 740
    p_draw.rectangle([40, 40, 40 + photo_w, 40 + photo_h], fill=(245, 242, 235, 255), outline=(215, 210, 200, 255), width=1)
    p = prod_img.copy()
    p.thumbnail((photo_w - 40, photo_h - 40), Image.Resampling.LANCZOS)
    pol.alpha_composite(p, (40 + (photo_w - p.width)//2, 40 + (photo_h - p.height)//2))
    
    draw_safe_text(p_draw, t, FONT_TITLE_SERIF, (35, 33, 30, 255), 740, 40, 810)
    draw_safe_text(p_draw, "★ AUTHENTIC RETRO NOSTALGIA ★", FONT_SANS_MED, (140, 90, 40, 255), 740, 40, 875)
    base.alpha_composite(pol, (px, py))
    
    draw_luxury_button(base, draw, 1180, c["btn_text"], (120, 65, 30, 255))
    draw_ftc(draw, 1275, color=(120, 112, 98, 255))
    return base.convert("RGB")

# 3. Dark Luxury Editorial
def t3_editorial(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title).upper()
    base = Image.new("RGBA", (W, H), (22, 24, 28, 255))
    draw = ImageDraw.Draw(base)
    
    draw.line([(60, 60), (W - 60, 60)], fill=(65, 70, 80, 255), width=1)
    draw.text((60, 70), "CURATED APPAREL // VOL. 26", font=FONT_SANS_SMALL, fill=(180, 185, 195, 255))
    draw.text((W - 220, 70), "AUTUMN / WINTER", font=FONT_SANS_SMALL, fill=(180, 185, 195, 255))
    draw.line([(60, 95), (W - 60, 95)], fill=(65, 70, 80, 255), width=1)
    
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (255, 255, 255, 255), 880, 60, 115, align="left")
    draw.text((60, 168), c["sub"].upper(), font=FONT_SANS_SMALL, fill=(215, 165, 95, 255))
    
    card_w, card_h = 880, 860
    cx, cy = 60, 215
    draw.rectangle([cx, cy, cx + card_w, cy + card_h], fill=(255, 255, 255, 255))
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    base.alpha_composite(p, (cx + (card_w - p.width)//2, cy + (card_h - p.height)//2))
    
    draw.line([(60, 1115), (W - 60, 1115)], fill=(65, 70, 80, 255), width=1)
    draw.text((60, 1125), "★ ★ ★ ★ ★  TOP TRENDING FASHION PICK", font=FONT_SANS_SMALL, fill=(245, 166, 35, 255))
    draw.text((W - 260, 1125), "AUTHENTIC ON AMAZON", font=FONT_SANS_SMALL, fill=(160, 165, 175, 255))
    
    draw_luxury_button(base, draw, 1175, c["btn_text"], (215, 165, 95, 255))
    draw_ftc(draw, 1270, color=(130, 135, 145, 255))
    return base.convert("RGB")

# 4. Boutique Spec Card
def t4_boutique(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (250, 248, 244, 255))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([35, 35, W - 35, H - 35], radius=16, outline=(225, 218, 205, 255), width=1)
    
    draw.text((65, 65), "CURATED WARDROBE PIECE", font=FONT_SANS_SMALL, fill=(140, 130, 115, 255))
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (35, 32, 28, 255), 870, 65, 95, align="left")
    draw_safe_text(draw, c["sub"], FONT_SUB_SERIF, (110, 102, 92, 255), 870, 65, 145, align="left")
    
    card_w, card_h = 870, 770
    cx, cy = 65, 195
    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    c_draw = ImageDraw.Draw(card)
    c_draw.rounded_rectangle([0, 0, card_w, card_h], radius=18, outline=(238, 232, 222, 255), width=1)
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))
    
    # Specs checklist
    draw.line([(65, 1000), (W - 65, 1000)], fill=(225, 218, 205, 255), width=1)
    draw.text((65, 1020), "✔ Verified Soft Touch Fabric", font=FONT_SANS_MED, fill=(50, 45, 40, 255))
    draw.text((365, 1020), "✔ Multiple Sizes & Colors", font=FONT_SANS_MED, fill=(50, 45, 40, 255))
    draw.text((675, 1020), "✔ Top Buyer Rated", font=FONT_SANS_MED, fill=(50, 45, 40, 255))
    draw.line([(65, 1060), (W - 65, 1060)], fill=(225, 218, 205, 255), width=1)
    
    draw.text((65, 1090), "★★★★★  Top Rated Amazon Fashion Pick", font=FONT_SANS_MED, fill=(215, 135, 25, 255))
    draw_luxury_button(base, draw, 1165, c["btn_text"], (35, 40, 45, 255))
    draw_ftc(draw, 1260)
    return base.convert("RGB")

# 5. Festive Gift Selection
def t5_festive(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (254, 252, 248, 255))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([35, 35, W - 35, H - 35], radius=22, outline=(175, 40, 40, 255), width=2)
    draw.rounded_rectangle([43, 43, W - 43, H - 43], radius=18, outline=(225, 205, 165, 255), width=1)
    
    b_bb = FONT_SANS_SMALL.getbbox("✨ 2026 GIFT SELECTION ✨")
    bw = b_bb[2] - b_bb[0] + 36
    draw.rounded_rectangle([(W - bw)//2, 65, (W + bw)//2, 98], radius=16, fill=(160, 30, 30, 255))
    draw.text(((W - (b_bb[2]-b_bb[0]))//2, 72), "✨ 2026 GIFT SELECTION ✨", font=FONT_SANS_SMALL, fill=(255, 245, 220, 255))
    
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (35, 30, 28, 255), 840, 80, 115)
    draw_safe_text(draw, c["sub"], FONT_SUB_SERIF, (140, 50, 50, 255), 840, 80, 168)
    
    card_w, card_h = 820, 860
    cx, cy = (W - card_w)//2, 225
    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))
    
    draw.text((cx + 170, 1125), "★★★★★", font=FONT_STARS, fill=(245, 166, 35, 255))
    draw.text((cx + 295, 1128), "Verified Holiday Gift Pick", font=FONT_SANS_MED, fill=(70, 65, 58, 255))
    draw_luxury_button(base, draw, 1180, c["btn_text"], (160, 30, 30, 255))
    draw_ftc(draw, 1270, color=(140, 125, 115, 255))
    return base.convert("RGB")

# 6. Scandinavian Minimalist
def t6_scandinavian(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (252, 252, 250, 255))
    draw = ImageDraw.Draw(base)
    
    draw.text((80, 75), f"CURATED NO. 06  //  {c['board_name'].upper()}", font=FONT_SANS_SMALL, fill=(140, 140, 140, 255))
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (25, 25, 25, 255), 840, 80, 105, align="left")
    draw_safe_text(draw, c["sub"], FONT_SUB_SERIF, (110, 110, 110, 255), 840, 80, 155, align="left")
    
    card_w, card_h = 840, 870
    cx, cy = 80, 210
    draw.rectangle([cx, cy, cx + card_w, cy + card_h], fill=(255, 255, 255, 255), outline=(235, 235, 232, 255), width=1)
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    base.alpha_composite(p, (cx + (card_w - p.width)//2, cy + (card_h - p.height)//2))
    
    draw.text((80, 1115), "RATING: ★ ★ ★ ★ ★ (VERIFIED BUYERS)", font=FONT_SANS_SMALL, fill=(80, 80, 80, 255))
    draw.text((W - 270, 1115), "AUTHENTIC ON AMAZON", font=FONT_SANS_SMALL, fill=(60, 120, 60, 255))
    draw_luxury_button(base, draw, 1170, c["btn_text"], (30, 30, 30, 255))
    draw_ftc(draw, 1265, color=(150, 150, 150, 255))
    return base.convert("RGB")

# 7. Outfit Styling Moodboard
def t7_moodboard(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (248, 245, 240, 255))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([35, 35, W - 35, H - 35], radius=20, outline=(225, 218, 205, 255), width=1)
    
    draw.text((65, 65), "HOW TO STYLE THIS PIECE", font=FONT_SANS_SMALL, fill=(140, 130, 115, 255))
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (35, 32, 28, 255), 870, 65, 95, align="left")
    draw_safe_text(draw, c["sub"], FONT_SUB_SERIF, (110, 102, 92, 255), 870, 65, 145, align="left")
    
    card_w, card_h = 870, 760
    cx, cy = 65, 195
    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))
    
    # Clean styling formula
    f_label = c.get("formula_label", "OUTFIT STYLING FORMULA:")
    f_text = c.get("formula", "• High quality materials  • Top verified customer reviews  • Fast Prime shipping")
    draw.line([(65, 990), (W - 65, 990)], fill=(225, 218, 205, 255), width=1)
    draw.text((65, 1005), f_label, font=FONT_SANS_MED, fill=(140, 85, 35, 255))
    draw_safe_text(draw, f_text, FONT_SUB_SERIF, (55, 50, 45, 255), 870, 65, 1035, align="left")
    
    draw_luxury_button(base, draw, 1165, c.get("btn_text", "VIEW DETAILS ON AMAZON ↗"), c["btn_color"])
    draw_ftc(draw, 1260)
    return base.convert("RGB")

# 8. Artisan Curated Lookbook (Replaces clunky scrapbook tape)
def t8_artisan(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (242, 238, 230, 255))
    draw = ImageDraw.Draw(base)
    
    draw.text((80, 65), f"★ {c['badge']} ★", font=FONT_SANS_SMALL, fill=(130, 85, 35, 255))
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (35, 30, 25, 255), 840, 80, 95, align="left")
    draw_safe_text(draw, c["sub"], FONT_SUB_SERIF, (115, 105, 90, 255), 840, 80, 145, align="left")
    
    card_w, card_h = 840, 840
    cx, cy = 80, 205
    card = Image.new("RGBA", (card_w, card_h), (255, 254, 250, 255))
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))
    
    draw.line([(80, 1080), (W - 80, 1080)], fill=(215, 205, 190, 255), width=1)
    draw_safe_text(draw, "“Effortless daily staple. Super soft feel with authentic streetwear drape.”", FONT_SUB_ITALIC, (85, 75, 65, 255), 840, 80, 1105)
    
    draw_luxury_button(base, draw, 1175, c["btn_text"], (120, 65, 30, 255))
    draw_ftc(draw, 1270, color=(130, 120, 105, 255))
    return base.convert("RGB")

# 9. Modern Tech Streetwear (Replaces chunky cyber Y2K with Off-White style)
def t9_tech_streetwear(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title).upper()
    base = Image.new("RGBA", (W, H), (18, 20, 24, 255))
    draw = ImageDraw.Draw(base)
    
    draw.rectangle([45, 45, W - 45, H - 45], outline=(55, 60, 70, 255), width=1)
    draw.text((70, 70), f"ARCHIVE // {c['board_name'].upper()}", font=FONT_SANS_SMALL, fill=(200, 255, 0, 255))
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (255, 255, 255, 255), 860, 70, 100, align="left")
    draw_safe_text(draw, c["sub"].upper(), FONT_SANS_SMALL, (150, 155, 165, 255), 860, 70, 150, align="left")
    
    card_w, card_h = 860, 860
    cx, cy = 70, 205
    draw.rectangle([cx, cy, cx + card_w, cy + card_h], fill=(255, 255, 255, 255))
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    base.alpha_composite(p, (cx + (card_w - p.width)//2, cy + (card_h - p.height)//2))
    
    draw.text((70, 1105), "SPEC: VERIFIED QUALITY • TOP TRENDING ON AMAZON", font=FONT_SANS_SMALL, fill=(200, 255, 0, 255))
    draw_luxury_button(base, draw, 1165, "GET THE FIT ON AMAZON ↗", (200, 255, 0, 255))
    # Black text on neon button
    c_bb = FONT_SANS_BOLD.getbbox("GET THE FIT ON AMAZON ↗")
    draw.text(((W - (c_bb[2]-c_bb[0]))//2, 1185), "GET THE FIT ON AMAZON ↗", font=FONT_SANS_BOLD, fill=(18, 20, 24, 255))
    draw_ftc(draw, 1260, color=(130, 135, 145, 255))
    return base.convert("RGB")

# 10. Verified Buyer Review (FIXED: Safe multi-line text wrapping)
def t10_review_spotlight(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (252, 250, 246, 255))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([35, 35, W - 35, H - 35], radius=20, outline=(225, 218, 205, 255), width=1)
    
    draw.text((70, 65), "★★★★★  OVER 1,000+ TOP RATINGS ON AMAZON", font=FONT_SANS_SMALL, fill=(215, 135, 25, 255))
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (35, 32, 28, 255), 860, 70, 95, align="left")
    
    card_w, card_h = 860, 750
    cx, cy = 70, 175
    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))
    
    # Safe Multi-Line Review Box
    draw.line([(70, 965), (W - 70, 965)], fill=(225, 218, 205, 255), width=1)
    draw.text((70, 975), "“", font=FONT_QUOTE_BIG, fill=(215, 160, 95, 255))
    # Draw wrapped quote safely within 760px
    end_qy = draw_safe_text(draw, c["quote"], FONT_SUB_SERIF, (45, 40, 35, 255), 760, 130, 995, align="left")
    draw.text((130, end_qy + 4), "— Verified Amazon Buyer  •  5.0 ★ Rating", font=FONT_SANS_SMALL, fill=(120, 110, 95, 255))
    
    draw_luxury_button(base, draw, 1165, "READ REVIEWS & SIZES ON AMAZON ↗", (45, 55, 72, 255))
    draw_ftc(draw, 1260)
    return base.convert("RGB")

# 11. Soft Sage & Sand Split
def t11_sage_split(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (250, 248, 244, 255))
    draw = ImageDraw.Draw(base)
    draw.rectangle([0, 0, W, 460], fill=(228, 234, 226, 255))
    
    draw.text((70, 65), f"AESTHETIC WARDROBE // {c['badge']}", font=FONT_SANS_SMALL, fill=(75, 95, 75, 255))
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (35, 45, 35, 255), 860, 70, 95, align="left")
    draw_safe_text(draw, c["sub"], FONT_SUB_SERIF, (85, 105, 85, 255), 860, 70, 145, align="left")
    
    card_w, card_h = 860, 850
    cx, cy = 70, 215
    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))
    
    draw.text((cx + 190, 1110), "★★★★★", font=FONT_STARS, fill=(245, 166, 35, 255))
    draw.text((cx + 315, 1113), "Curated Style Essential", font=FONT_SANS_MED, fill=(75, 95, 75, 255))
    draw_luxury_button(base, draw, 1165, c["btn_text"], (85, 115, 85, 255))
    draw_ftc(draw, 1260, color=(130, 140, 130, 255))
    return base.convert("RGB")

# 12. Monochrome High Fashion (Clean & minimal, no harsh heavy bars)
def t12_monochrome(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title).upper()
    base = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(base)
    
    draw.line([(60, 60), (W - 60, 60)], fill=(0, 0, 0, 255), width=2)
    draw.text((60, 70), f"OBJECT ARCHIVE // {c['board_name'].upper()}", font=FONT_SANS_SMALL, fill=(0, 0, 0, 255))
    draw.line([(60, 95), (W - 60, 95)], fill=(0, 0, 0, 255), width=1)
    
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (0, 0, 0, 255), 880, 60, 115, align="left")
    draw.text((60, 165), c["sub"].upper(), font=FONT_SANS_SMALL, fill=(120, 120, 120, 255))
    
    card_w, card_h = 880, 860
    cx, cy = 60, 215
    draw.rectangle([cx, cy, cx + card_w, cy + card_h], fill=(250, 250, 250, 255), outline=(230, 230, 230, 255), width=1)
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    base.alpha_composite(p, (cx + (card_w - p.width)//2, cy + (card_h - p.height)//2))
    
    draw.line([(60, 1115), (W - 60, 1115)], fill=(0, 0, 0, 255), width=1)
    draw.text((60, 1125), "ITEM CODE: 2026-AMZ-DROP // 100% VERIFIED", font=FONT_SANS_SMALL, fill=(0, 0, 0, 255))
    draw.text((W - 240, 1125), "★ ★ ★ ★ ★ RATED", font=FONT_SANS_SMALL, fill=(0, 0, 0, 255))
    
    draw_luxury_button(base, draw, 1175, "VIEW PIECE ON AMAZON ↗", (0, 0, 0, 255))
    draw_ftc(draw, 1270, color=(120, 120, 120, 255))
    return base.convert("RGB")

# 13. Warm Boho Terracotta
def t13_terracotta(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (218, 138, 112, 255))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([35, 35, W - 35, H - 35], radius=24, outline=(245, 230, 220, 255), width=2)
    
    draw_safe_text(draw, f"• {c['badge']} •", FONT_SANS_MED, (255, 245, 235, 255), 840, 80, 65)
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (255, 255, 255, 255), 840, 80, 100)
    draw_safe_text(draw, c["sub"], FONT_SUB_SERIF, (250, 225, 215, 255), 840, 80, 155)
    
    card_w, card_h = 860, 850
    cx, cy = 70, 215
    card = Image.new("RGBA", (card_w, card_h), (255, 253, 250, 255))
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))
    
    draw.text((cx + 190, 1110), "★★★★★", font=FONT_STARS, fill=(255, 245, 220, 255))
    draw.text((cx + 315, 1113), "Boho Autumn Essential", font=FONT_SANS_MED, fill=(255, 245, 235, 255))
    draw_luxury_button(base, draw, 1165, c["btn_text"], (85, 45, 35, 255))
    draw_ftc(draw, 1260, color=(245, 220, 210, 255))
    return base.convert("RGB")

# 14. Cinematic Lookbook (Clean film letterbox, NO clunky sprocket holes)
def t14_cinematic(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (22, 20, 20, 255))
    draw = ImageDraw.Draw(base)
    
    draw.line([(60, 60), (W - 60, 60)], fill=(75, 70, 65, 255), width=1)
    draw.text((60, 70), "CINEMATIC 35MM ARCHIVE // NO. 24", font=FONT_SANS_SMALL, fill=(225, 175, 90, 255))
    draw.text((W - 200, 70), "FRAME ISO 400", font=FONT_SANS_SMALL, fill=(180, 175, 165, 255))
    draw.line([(60, 95), (W - 60, 95)], fill=(75, 70, 65, 255), width=1)
    
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (255, 255, 255, 255), 880, 60, 115, align="left")
    draw_safe_text(draw, c["sub"], FONT_SUB_SERIF, (180, 175, 165, 255), 880, 60, 160, align="left")
    
    card_w, card_h = 880, 860
    cx, cy = 60, 215
    draw.rectangle([cx, cy, cx + card_w, cy + card_h], fill=(255, 255, 255, 255))
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    base.alpha_composite(p, (cx + (card_w - p.width)//2, cy + (card_h - p.height)//2))
    
    draw.line([(60, 1115), (W - 60, 1115)], fill=(75, 70, 65, 255), width=1)
    draw.text((60, 1125), "★ ★ ★ ★ ★ VINTAGE NOSTALGIA DROP • AMAZON AUTHENTIC", font=FONT_SANS_SMALL, fill=(225, 175, 90, 255))
    draw_luxury_button(base, draw, 1175, "EXPLORE RETRO DROP ON AMAZON ↗", (215, 155, 65, 255))
    # Dark text on amber button
    c_bb = FONT_SANS_BOLD.getbbox("EXPLORE RETRO DROP ON AMAZON ↗")
    draw.text(((W - (c_bb[2]-c_bb[0]))//2, 1195), "EXPLORE RETRO DROP ON AMAZON ↗", font=FONT_SANS_BOLD, fill=(22, 20, 20, 255))
    draw_ftc(draw, 1270, color=(140, 135, 130, 255))
    return base.convert("RGB")

# 15. Haute Boutique Tag
def t15_haute_boutique(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (252, 250, 246, 255))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([35, 35, W - 35, H - 35], radius=20, outline=(225, 218, 205, 255), width=1)
    
    draw.text((65, 65), "BOUTIQUE CATALOG // AUTHENTIC", font=FONT_SANS_SMALL, fill=(45, 55, 72, 255))
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (30, 30, 30, 255), 870, 65, 95, align="left")
    draw_safe_text(draw, c["sub"], FONT_SUB_SERIF, (120, 115, 105, 255), 870, 65, 145, align="left")
    
    card_w, card_h = 870, 780
    cx, cy = 65, 200
    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    c_draw = ImageDraw.Draw(card)
    c_draw.rounded_rectangle([0, 0, card_w, card_h], radius=20, outline=(235, 228, 218, 255), width=1)
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))
    
    draw.line([(65, 1020), (W - 65, 1020)], fill=(225, 218, 205, 255), width=1)
    draw.text((65, 1040), "✔ Verified Soft Fabric   ✔ Multiple Sizes Available   ✔ Top Buyer Rated", font=FONT_SANS_MED, fill=(55, 65, 80, 255))
    draw.text((65, 1085), "★★★★★ (4.8 / 5.0) Amazon Customer Choice", font=FONT_SANS_MED, fill=(215, 135, 25, 255))
    
    draw_luxury_button(base, draw, 1165, c["btn_text"], (45, 55, 72, 255))
    draw_ftc(draw, 1260)
    return base.convert("RGB")

# 16. Pet Parent Boutique
def t16_pet_boutique(prod_img, title, board_id):
    W, H = 1000, 1500
    c = BOARD_COPY.get(str(board_id), DEFAULT_C)
    t = clean_title(title)
    base = Image.new("RGBA", (W, H), (254, 250, 240, 255))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([35, 35, W - 35, H - 35], radius=24, outline=(235, 195, 130, 255), width=2)
    
    is_pet = any(k in (c.get("badge", "") + " " + c.get("board_name", "")).upper() for k in ["PET", "CAT", "DOG"])
    pet_badge = "🐾 PET PARENT APPROVED 🐾" if is_pet else "✨ CURATED GIFT FAVORITE ✨"
    pet_sub = "The Sweetest Gift for Dog & Cat Lovers" if is_pet else c["sub"]
    pet_proof = "Loved by 1,000+ Pet Parents" if is_pet else "Loved by 1,000+ Verified Buyers"
    
    b_bb = FONT_SANS_SMALL.getbbox(pet_badge)
    bw = b_bb[2] - b_bb[0] + 36
    draw.rounded_rectangle([(W - bw)//2, 65, (W + bw)//2, 98], radius=16, fill=(195, 120, 30, 255))
    draw.text(((W - (b_bb[2]-b_bb[0]))//2, 72), pet_badge, font=FONT_SANS_SMALL, fill=(255, 255, 255, 255))
    
    draw_safe_text(draw, t, FONT_TITLE_SERIF, (45, 35, 25, 255), 840, 80, 115)
    draw_safe_text(draw, pet_sub, FONT_SUB_SERIF, (150, 95, 35, 255), 840, 80, 168)
    
    card_w, card_h = 820, 860
    cx, cy = (W - card_w)//2, 225
    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    p = prod_img.copy()
    p.thumbnail((card_w - 60, card_h - 60), Image.Resampling.LANCZOS)
    card.alpha_composite(p, ((card_w - p.width)//2, (card_h - p.height)//2))
    base.alpha_composite(card, (cx, cy))
    
    draw.text((cx + 170, 1125), "★★★★★", font=FONT_STARS, fill=(245, 166, 35, 255))
    draw.text((cx + 295, 1128), pet_proof, font=FONT_SANS_MED, fill=(130, 80, 25, 255))
    draw_luxury_button(base, draw, 1180, c["btn_text"], (195, 120, 30, 255))
    draw_ftc(draw, 1270, color=(150, 140, 125, 255))
    return base.convert("RGB")

# -------------------------------------------------------------
# Complete 16 Handcrafted Luxury Registry
# -------------------------------------------------------------
REFINED_16_MAP = {
    0: ("Warm Linen Studio", t1_linen_studio),
    1: ("Vintage 90s Polaroid", t2_polaroid),
    2: ("Dark Luxury Editorial", t3_editorial),
    3: ("Boutique Spec Card", t4_boutique),
    4: ("Festive Gift Selection", t5_festive),
    5: ("Scandinavian Minimalist", t6_scandinavian),
    6: ("Outfit Styling Moodboard", t7_moodboard),
    7: ("Artisan Curated Lookbook", t8_artisan),
    8: ("Modern Tech Streetwear", t9_tech_streetwear),
    9: ("Verified Buyer Review", t10_review_spotlight),
    10: ("Soft Sage Sand Split", t11_sage_split),
    11: ("Monochrome High Fashion", t12_monochrome),
    12: ("Warm Boho Terracotta", t13_terracotta),
    13: ("Cinematic Lookbook 35mm", t14_cinematic),
    14: ("Haute Boutique Tag", t15_haute_boutique),
    15: ("Pet Parent Boutique", t16_pet_boutique)
}

BOARD_ROTATION_MAP = {
    "1093037840753522205": [0, 6, 1, 8, 10, 11, 7, 14],   # Graphic Tees
    "1093037840753522206": [2, 0, 8, 9, 11, 3, 6, 12],     # Hoodies
    "1093037840753522208": [15, 3, 9, 4, 0, 7, 10, 14],    # Pet Gifts
    "1093037840753522209": [5, 9, 0, 10, 3, 6, 12, 14],    # Viral Fashion
    "1093037840753522211": [1, 13, 7, 2, 8, 12, 11, 0],    # Vintage 90s
    "1093037840753522212": [4, 0, 9, 3, 10, 14, 5, 2]      # Holiday Sweaters
}

def generate_audited_16_pin(product_image_url, title, board_id, template_idx=0):
    resp = requests.get(product_image_url, timeout=15)
    prod_img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    t_name, t_fn = REFINED_16_MAP[template_idx % len(REFINED_16_MAP)]
    return t_fn(prod_img, title, board_id), t_name

def generate_audited_16_base64(product_image_url, title, board_id, queue_index=1):
    pref_list = BOARD_ROTATION_MAP.get(str(board_id), list(range(16)))
    cycle = (queue_index - 1) // 6
    template_idx = pref_list[cycle % len(pref_list)]
    img, t_name = generate_audited_16_pin(product_image_url, title, board_id, template_idx)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return base64.b64encode(buf.getvalue()).decode("utf-8"), t_name

if __name__ == "__main__":
    test_img = "https://m.media-amazon.com/images/I/811O9zF0kZL.jpg"
    print("Testing and rendering all 16 refined luxury templates...")
    # Fetch test image once
    resp = requests.get(test_img, timeout=15)
    p_img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    
    for idx in range(16):
        t_name, t_fn = REFINED_16_MAP[idx]
        img = t_fn(p_img, "Oversized Cable Knit Sweater", "1093037840753522209")
        out = f"luxury_template_{idx+1}.jpg"
        img.save(out, quality=95)
        print(f"✔ Rendered #{idx+1}: {t_name} -> {out}")
