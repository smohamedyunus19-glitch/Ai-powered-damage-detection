from flask import Blueprint, request, jsonify, current_app
from models.damage_model import predict_damage
from models.db_models import prediction_schema
import os
import cv2

predict_bp = Blueprint("predict", __name__)


def validate_device_image(image_path, device_type):
    """
    Image-ல இருக்குற device, select பண்ணின device-ஓட match ஆகுதான்னு check பண்ணு.
    
    Logic:
    - Phone image → Portrait (height > width) → ratio < 0.85
    - Laptop image → Landscape (width > height) → ratio > 1.0
    """
    img = cv2.imread(image_path)
    if img is None:
        return True, None  # Read பண்ண முடியல — pass பண்ணிடு

    h, w = img.shape[:2]
    ratio = w / h  # width ÷ height

    if device_type == "mobile" and ratio > 1.2:
        return False, (
            "❌ நீங்கள் Laptop image upload பண்ணீர்கள்! "
            "Mobile phone-ஓட damage photo upload பண்ணுங்கள்."
        )

    if device_type == "laptop" and ratio < 0.75:
        return False, (
            "❌ நீங்கள் Mobile phone image upload பண்ணீர்கள்! "
            "Laptop-ஓட damage photo upload பண்ணுங்கள்."
        )

    return True, None


@predict_bp.route("/predict", methods=["POST"])
def predict():
    """
    POST /api/predict
    JSON Body:
    {
        "filename": "abc123.jpg",
        "device_type": "mobile",
        "latitude": 9.9252,      (optional)
        "longitude": 78.1198     (optional)
    }

    Response:
    {
        "success": true,
        "device_type": "mobile",
        "damage_type": "crack",
        "severity": "high",
        "confidence": 0.91,
        "prediction_id": "mongo_id"
    }
    """
    from app import db

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "JSON body required"}), 400

    filename    = data.get("filename")
    device_type = data.get("device_type", "").lower()
    latitude    = data.get("latitude")
    longitude   = data.get("longitude")

    # Basic Validation
    if not filename or not device_type:
        return jsonify({"success": False, "error": "filename and device_type required"}), 400

    if device_type not in ["mobile", "laptop"]:
        return jsonify({"success": False, "error": "device_type must be 'mobile' or 'laptop'"}), 400

    image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(image_path):
        return jsonify({"success": False, "error": "Image not found. Upload first."}), 404

    # ✅ Device Type Validation — Wrong device image-ஐ reject பண்ணு
    is_valid, error_msg = validate_device_image(image_path, device_type)
    if not is_valid:
        return jsonify({
            "success": False,
            "error": error_msg,
            "error_type": "wrong_device"
        }), 400

    # AI Prediction
    result = predict_damage(image_path, device_type)

    # MongoDB Save
    record = prediction_schema(
        image_filename=filename,
        device_type=device_type,
        damage_type=result["damage_type"],
        severity=result["severity"],
        confidence=result["confidence"],
        latitude=latitude,
        longitude=longitude
    )
    inserted = db.predictions.insert_one(record)

    return jsonify({
        "success": True,
        "prediction_id": str(inserted.inserted_id),
        "device_type": device_type,
        "damage_type": result["damage_type"],
        "severity": result["severity"],
        "confidence": result["confidence"],
        "all_detections": result["all_detections"],
        "message": f"{device_type.capitalize()} damage detected ✅"
    }), 200
