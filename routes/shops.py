from flask import Blueprint, request, jsonify
import requests

shops_bp = Blueprint('shops', __name__)

@shops_bp.route('/shops', methods=['GET'])
def get_shops():
    lat = float(request.args.get('lat', 13.0827))
    lng = float(request.args.get('lng', 80.2707))
    device_type = request.args.get('device_type', 'mobile')

    # Overpass API — multiple shop types search
    overpass_url = "http://overpass-api.de/api/interpreter"

    if device_type == 'mobile':
        # Mobile repair shops — wider search
        query = f"""
        [out:json][timeout:15];
        (
          node["shop"="mobile_phone"](around:5000,{lat},{lng});
          node["shop"="electronics"](around:5000,{lat},{lng});
          node["repair"="electronics"](around:5000,{lat},{lng});
          node["shop"="computer"](around:5000,{lat},{lng});
          node["name"~"mobile|phone|repair|fix",i](around:5000,{lat},{lng});
        );
        out body;
        """
    else:
        # Laptop repair shops
        query = f"""
        [out:json][timeout:15];
        (
          node["shop"="computer"](around:5000,{lat},{lng});
          node["shop"="electronics"](around:5000,{lat},{lng});
          node["repair"="electronics"](around:5000,{lat},{lng});
          node["name"~"laptop|computer|tech|repair|service",i](around:5000,{lat},{lng});
        );
        out body;
        """

    try:
        response = requests.get(
            overpass_url,
            params={'data': query},
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        shops = []
        seen = set()  # Duplicate remove

        for element in data.get('elements', []):
            tags = element.get('tags', {})
            name = tags.get('name', '').strip()

            # Name இல்லாத shops skip பண்ணு
            if not name or name in seen:
                continue
            seen.add(name)

            # Address build பண்ணு
            addr_parts = []
            for key in ['addr:housenumber', 'addr:street', 'addr:suburb', 'addr:city']:
                val = tags.get(key, '')
                if val:
                    addr_parts.append(val)

            address = ', '.join(addr_parts) if addr_parts else tags.get('addr:full', 'Address not available')

            # Phone
            phone = tags.get('phone') or tags.get('contact:phone') or tags.get('mobile') or 'Not available'

            shops.append({
                "name": name,
                "address": address,
                "phone": phone,
                "latitude": element.get('lat'),
                "longitude": element.get('lon'),
                "open_now": None,
                "rating": None
            })

            if len(shops) >= 6:
                break

        # Real shops இல்லன்னா mock data
        if not shops:
            print(f"[SHOPS] No real shops found at lat={lat}, lng={lng}. Using mock.")
            shops = get_mock_shops(device_type)

        return jsonify({
            "success": True,
            "shops": shops,
            "total": len(shops),
            "source": "openstreetmap" if shops else "mock"
        })

    except requests.exceptions.Timeout:
        print("[SHOPS] Overpass API timeout")
        return jsonify({"success": True, "shops": get_mock_shops(device_type), "total": 2, "source": "mock"})

    except Exception as e:
        print(f"[SHOPS] Error: {e}")
        return jsonify({"success": True, "shops": get_mock_shops(device_type), "total": 2, "source": "mock"})


def get_mock_shops(device_type):
    """Fallback mock shops — real API fail ஆனா இது வரும்"""
    if device_type == 'mobile':
        return [
            {
                "name": "Mobile Care Service",
                "address": "Anna Salai, Chennai",
                "phone": "+91 98765 43210",
                "open_now": True,
                "rating": 4.5
            },
            {
                "name": "Phone Fix Expert",
                "address": "T Nagar, Chennai",
                "phone": "+91 87654 32109",
                "open_now": True,
                "rating": 4.2
            },
        ]
    else:
        return [
            {
                "name": "Laptop World Service",
                "address": "Nungambakkam, Chennai",
                "phone": "+91 98654 32101",
                "open_now": True,
                "rating": 4.6
            },
            {
                "name": "Tech Fix Solutions",
                "address": "Adyar, Chennai",
                "phone": "+91 87543 21090",
                "open_now": False,
                "rating": 4.3
            },
        ]
