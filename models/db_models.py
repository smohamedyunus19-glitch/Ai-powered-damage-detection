from datetime import datetime

# ─────────────────────────────────────────
# Prediction Record — MongoDB Schema
# ─────────────────────────────────────────
def prediction_schema(
    image_filename: str,
    device_type: str,       # "mobile" or "laptop"
    damage_type: str,       # "crack", "scratch", "broken", etc.
    severity: str,          # "low", "medium", "high"
    confidence: float,      # Model confidence score
    latitude: float = None,
    longitude: float = None
) -> dict:
    return {
        "image_filename": image_filename,
        "device_type": device_type,
        "damage_type": damage_type,
        "severity": severity,
        "confidence": round(confidence, 4),
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "created_at": datetime.utcnow()
    }


# ─────────────────────────────────────────
# Shop Record — MongoDB Schema
# ─────────────────────────────────────────
def shop_schema(
    name: str,
    address: str,
    phone: str,
    rating: float,
    latitude: float,
    longitude: float,
    place_id: str
) -> dict:
    return {
        "place_id": place_id,
        "name": name,
        "address": address,
        "phone": phone,
        "rating": rating,
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "cached_at": datetime.utcnow()
    }
