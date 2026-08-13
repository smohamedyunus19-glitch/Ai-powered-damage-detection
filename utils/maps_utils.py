import requests
from config import Config

PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# ─────────────────────────────────────────
# Device → Repair Shop Search Query
# ─────────────────────────────────────────
DEVICE_QUERY_MAP = {
    "mobile": "mobile repair shop",
    "laptop": "laptop repair shop",
    "general": "electronics repair shop"
}


# ─────────────────────────────────────────
# Nearby Shops Fetch
# ─────────────────────────────────────────
def get_nearby_shops(latitude: float, longitude: float, device_type: str, radius: int = 5000) -> list:
    """
    Google Places API-ல nearby repair shops fetch பண்ணும்
    radius: meters (default 5km)
    """
    keyword = DEVICE_QUERY_MAP.get(device_type, "electronics repair shop")

    params = {
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "keyword": keyword,
        "key": Config.GOOGLE_PLACES_API_KEY
    }

    response = requests.get(PLACES_URL, params=params)
    data = response.json()

    if data.get("status") != "OK":
        return []

    shops = []
    for place in data.get("results", [])[:5]:  # Top 5 shops மட்டும்
        shop = {
            "place_id": place.get("place_id"),
            "name": place.get("name"),
            "address": place.get("vicinity"),
            "rating": place.get("rating", "N/A"),
            "total_ratings": place.get("user_ratings_total", 0),
            "open_now": place.get("opening_hours", {}).get("open_now", None),
            "location": {
                "latitude": place["geometry"]["location"]["lat"],
                "longitude": place["geometry"]["location"]["lng"]
            }
        }

        # Phone number fetch பண்ணு (extra API call)
        phone = get_phone_number(place.get("place_id"))
        shop["phone"] = phone

        shops.append(shop)

    return shops


# ─────────────────────────────────────────
# Phone Number from Place ID
# ─────────────────────────────────────────
def get_phone_number(place_id: str) -> str:
    if not place_id:
        return "N/A"

    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number",
        "key": Config.GOOGLE_PLACES_API_KEY
    }

    response = requests.get(DETAILS_URL, params=params)
    data = response.json()

    return data.get("result", {}).get("formatted_phone_number", "N/A")
