from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# CORS — Frontend எந்த port-லயும் connect ஆகலாம்
CORS(app)

# MongoDB Connection
client = MongoClient(app.config["MONGO_URI"])
db = client.get_default_database()

# Upload folder create பண்ணு
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Routes import
from routes.upload import upload_bp
from routes.predict import predict_bp
from routes.shops import shops_bp
from routes.history import history_bp

app.register_blueprint(upload_bp,  url_prefix="/api")
app.register_blueprint(predict_bp, url_prefix="/api")
app.register_blueprint(shops_bp,   url_prefix="/api")
app.register_blueprint(history_bp, url_prefix="/api")

@app.route("/")
def index():
    return {"status": "Repair App Backend Running ✅", "version": "1.0.0"}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
