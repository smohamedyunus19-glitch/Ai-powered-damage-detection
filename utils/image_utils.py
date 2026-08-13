import os
import uuid
from PIL import Image
from config import Config

# ─────────────────────────────────────────
# Allowed File Check
# ─────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )


# ─────────────────────────────────────────
# Save Uploaded Image
# ─────────────────────────────────────────
def save_image(file) -> str:
    """
    Unique filename generate பண்ணி save பண்ணும்
    Returns: saved filename
    """
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
    file.save(save_path)
    return unique_name


# ─────────────────────────────────────────
# Resize Image for Model Input
# ─────────────────────────────────────────
def preprocess_image(image_path: str, size: tuple = (640, 640)) -> str:
    """
    YOLOv8-க்கு 640x640 optimal size
    Returns: preprocessed image path
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize(size)
    img.save(image_path)
    return image_path


# ─────────────────────────────────────────
# Delete Image after processing (optional)
# ─────────────────────────────────────────
def delete_image(filename: str):
    path = os.path.join(Config.UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
