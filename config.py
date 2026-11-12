import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parent
    ENV_PATH = BASE_DIR / ".env"
    load_dotenv(dotenv_path=ENV_PATH)
except ImportError:
    pass

# Pinterest Config
PINTEREST_APP_ID = os.getenv("PINTEREST_APP_ID", "")
PINTEREST_APP_SECRET = os.getenv("PINTEREST_APP_SECRET", "")
PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN", "")
PINTEREST_REFRESH_TOKEN = os.getenv("PINTEREST_REFRESH_TOKEN", "")

# Amazon SP-API / LWA Config
AMAZON_CLIENT_ID = os.getenv("AMAZON_CLIENT_ID", "")
AMAZON_CLIENT_SECRET = os.getenv("AMAZON_CLIENT_SECRET", "")
AMAZON_REFRESH_TOKEN = os.getenv("AMAZON_REFRESH_TOKEN", "")
AMAZON_MARKETPLACE_ID = os.getenv("AMAZON_MARKETPLACE_ID", "ATVPDKIKX0DER")

# Amazon Associate ID
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "mostefa-daoua-20")


# Valid Pinterest Interests / Categories
PINTEREST_INTERESTS = [
    "womens_fashion",
    "mens_fashion",
    "animals",
    "art",
    "design",
    "childrens_fashion",
    "home_decor",
    "beauty",
    "diy_and_crafts",
    "event_planning",
    "food_and_drinks",
    "gardening",
    "health",
    "parenting",
    "quotes",
    "sport",
    "travel",
    "vehicles",
    "wedding"
]
