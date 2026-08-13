from flask import Blueprint, request, jsonify, current_app
from utils.image_utils import allowed_file, save_image, preprocess_image
import os

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/upload", methods=["POST"])
def upload_image():
    """
    POST /api/upload
    Form-data: file (image), device_type (mobile/laptop)
    
    Response:
    {
        "success": true,
        "filename": "abc123.jpg",
        "device_type": "mobile"
    }
    """
    # File check
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400

    file = request.files["file"]
    device_type = request.form.get("device_type", "").lower()

    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"}), 400

    if device_type not in ["mobile", "laptop"]:
        return jsonify({"success": False, "error": "device_type must be 'mobile' or 'laptop'"}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Allowed formats: png, jpg, jpeg, webp"}), 400

    # Save & preprocess
    filename = save_image(file)
    image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    preprocess_image(image_path)

    return jsonify({
        "success": True,
        "filename": filename,
        "device_type": device_type,
        "message": "Image uploaded successfully ✅"
    }), 200
