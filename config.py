import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/repairapp")
    
    # Google Places API
    GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
    
    # File Upload
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    
    # ML Models Path
    MOBILE_MODEL_PATH = os.path.join("ml_models", "mobile_model.pt")
    LAPTOP_MODEL_PATH = os.path.join("ml_models", "laptop_model.pt")
