import time
import requests
from config import (
    AMAZON_CLIENT_ID,
    AMAZON_CLIENT_SECRET,
    AMAZON_REFRESH_TOKEN,
    AMAZON_ASSOCIATE_TAG,
    AMAZON_MARKETPLACE_ID
)

LWA_URL = "https://api.amazon.com/auth/o2/token"
SP_API_URL = "https://sellingpartnerapi-na.amazon.com"

class AmazonSPAPI:
    def __init__(self):
        self.client_id = AMAZON_CLIENT_ID
        self.client_secret = AMAZON_CLIENT_SECRET
        self.refresh_token = AMAZON_REFRESH_TOKEN
        self.associate_tag = AMAZON_ASSOCIATE_TAG
        self.marketplace_id = AMAZON_MARKETPLACE_ID

        self._access_token = None
        self._token_expires_at = 0

    def get_access_token(self):
        """Exchange LWA Refresh Token for a temporary SP-API Access Token"""
        # Return cached token if still valid (with 60-second buffer)
        if self._access_token and time.time() < (self._token_expires_at - 60):
            return self._access_token

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        resp = requests.post(LWA_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if resp.status_code == 200:
            res = resp.json()
            self._access_token = res["access_token"]
            expires_in = res.get("expires_in", 3600)
            self._token_expires_at = time.time() + expires_in
            return self._access_token
        raise Exception(f"Failed to refresh Amazon LWA token ({resp.status_code}): {resp.text}")

    def build_affiliate_link(self, asin):
        """Construct Amazon Affiliate Link with Associate Tracking Tag"""
        return f"https://www.amazon.com/dp/{asin}?tag={self.associate_tag}"

    def search_catalog(self, keywords, page_size=5):
        """
        Search Amazon product catalog by keywords.
        Returns a list of structured products with title, asin, image_url, and affiliate link.
        """
        access_token = self.get_access_token()
        url = f"{SP_API_URL}/catalog/2022-04-01/items"

        params = {
            "marketplaceIds": self.marketplace_id,
            "keywords": keywords,
            "includedData": "summaries,images",
            "pageSize": min(page_size, 20)
        }

        headers = {
            "x-amz-access-token": access_token,
            "User-Agent": "AntigravityAffiliateBot/1.0"
        }

        resp = requests.get(url, params=params, headers=headers)
        if resp.status_code != 200:
            raise Exception(f"Amazon Catalog Search error ({resp.status_code}): {resp.text}")

        data = resp.json()
        raw_items = data.get("items", [])
        products = []

        for item in raw_items:
            asin = item.get("asin")
            summaries = item.get("summaries", [])
            title = summaries[0].get("itemName", "") if summaries else ""
            brand = summaries[0].get("brand", "") if summaries else ""

            # Extract best image
            images_block = item.get("images", [])
            image_url = None
            if images_block:
                imgs = images_block[0].get("images", [])
                if imgs:
                    # Pick the largest image or first image
                    imgs_sorted = sorted(imgs, key=lambda x: x.get("width", 0), reverse=True)
                    image_url = imgs_sorted[0].get("link")

            if asin and image_url:
                products.append({
                    "asin": asin,
                    "title": title,
                    "brand": brand,
                    "image_url": image_url,
                    "affiliate_url": self.build_affiliate_link(asin)
                })

        return products
