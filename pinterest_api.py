import time
import requests
from config import PINTEREST_ACCESS_TOKEN

BASE_URL = "https://api.pinterest.com/v5"

class PinterestAPI:
    def __init__(self, token=None, sandbox=False):
        self.sandbox = sandbox
        self.base_url = "https://api-sandbox.pinterest.com/v5" if sandbox else "https://api.pinterest.com/v5"
        self.token = token or PINTEREST_ACCESS_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "MarryTreasuresStudio/1.0"
        }

    def get_user_account(self):
        """Fetch authenticated user profile details"""
        url = f"{self.base_url}/user_account"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            return resp.json()
        raise Exception(f"Pinterest user_account error ({resp.status_code}): {resp.text}")

    def get_boards(self, page_size=100):
        """Fetch all boards belonging to the user"""
        url = f"{self.base_url}/boards?page_size={page_size}"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            return resp.json().get("items", [])
        raise Exception(f"Pinterest boards error ({resp.status_code}): {resp.text}")

    def create_board(self, name, description=None, privacy="PUBLIC"):
        """Create a new board on Pinterest"""
        url = f"{self.base_url}/boards"
        payload = {
            "name": name[:50],
            "privacy": privacy
        }
        if description:
            payload["description"] = description[:500]

        resp = requests.post(url, json=payload, headers=self.headers)
        if resp.status_code in (200, 201):
            return resp.json()
        raise Exception(f"Pinterest create_board error ({resp.status_code}): {resp.text}")

    def get_trends(self, interest=None, trend_type="growing", region="US", limit=20):
        """
        Fetch trending keywords from Pinterest Trends API.
        trend_type: 'growing', 'monthly', 'yearly', 'seasonal'
        interest: e.g. 'womens_fashion', 'animals', 'art', etc.
        region: 'US', 'GB', 'CA', etc.
        """
        url = f"{self.base_url}/trends/keywords/{region}/top/{trend_type}"
        params = {}
        if interest:
            params["interests"] = interest
            params["normalize_against_group"] = "true"

        resp = requests.get(url, headers=self.headers, params=params)
        if resp.status_code == 200:
            data = resp.json().get("trends", [])
            return data[:limit]
        raise Exception(f"Pinterest trends error ({resp.status_code}): {resp.text}")

    def create_pin(self, title, description, link, board_id, image_url=None, image_base64=None, alt_text=None):
        """
        Create a new pin on a specific board using either an image URL or base64 data.
        Note: Requires 'pins:write' scope on the access token.
        """
        url = f"{self.base_url}/pins"
        payload = {
            "title": title[:100],  # Max 100 chars
            "description": description[:500],  # Max 500 chars
            "link": link,
            "board_id": str(board_id),
        }

        if image_base64:
            payload["media_source"] = {
                "source_type": "image_base64",
                "content_type": "image/jpeg",
                "data": image_base64
            }
        elif image_url:
            payload["media_source"] = {
                "source_type": "image_url",
                "url": image_url
            }
        else:
            raise ValueError("Either image_url or image_base64 must be provided")

        if alt_text:
            payload["alt_text"] = alt_text[:500]

        max_retries = 3
        last_err = None
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.post(url, json=payload, headers=self.headers, timeout=35)
                if resp.status_code in (200, 201):
                    return resp.json()
                elif resp.status_code == 401:
                    err = resp.json()
                    msg = err.get("message", resp.text)
                    raise PermissionError(f"Token lacks write permissions: {msg}")
                else:
                    raise Exception(f"Pinterest create_pin error ({resp.status_code}): {resp.text}")
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as net_err:
                last_err = net_err
                print(f"⚠️ Network timeout connecting to Pinterest API (attempt {attempt}/{max_retries}). Retrying in {attempt * 2}s...")
                time.sleep(attempt * 2)

        raise last_err
