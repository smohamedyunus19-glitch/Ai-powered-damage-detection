# 🔧 Repair App — Backend

Flask + MongoDB + YOLOv8 based damage detection backend.

## 📁 Project Structure
```
repair-app-backend/
├── app.py              → Main Flask app
├── config.py           → Settings & env vars
├── requirements.txt    → Dependencies
├── .env                → API keys (git-ignore பண்ணு!)
├── routes/
│   ├── upload.py       → POST /api/upload
│   ├── predict.py      → POST /api/predict
│   ├── shops.py        → GET  /api/shops
│   └── history.py      → GET  /api/history
├── models/
│   ├── damage_model.py → YOLOv8 loader & predictor
│   └── db_models.py    → MongoDB schemas
├── utils/
│   ├── image_utils.py  → Image save & preprocess
│   └── maps_utils.py   → Google Places API
└── ml_models/
    ├── mobile_model.pt → Train பண்ணி இங்க வை
    └── laptop_model.pt → Train பண்ணி இங்க வை
```

## 🚀 Setup & Run

### 1. Clone & Install
```bash
git clone <your-repo>
cd repair-app-backend
pip install -r requirements.txt
```

### 2. .env Configure பண்ணு
```
MONGO_URI=mongodb://localhost:27017/repairapp
GOOGLE_PLACES_API_KEY=your_key_here
```

### 3. Run
```bash
python app.py
```
Server: http://localhost:5000

---

## 📡 API Endpoints

### Upload Image
```
POST /api/upload
Form-data: file=<image>, device_type=mobile|laptop
```

### Predict Damage
```
POST /api/predict
JSON: { "filename": "abc.jpg", "device_type": "mobile", "latitude": 9.92, "longitude": 78.11 }
```

### Nearby Shops
```
GET /api/shops?lat=9.9252&lng=78.1198&device_type=mobile&radius=5000
```

### History
```
GET    /api/history?device_type=mobile&limit=10
GET    /api/history/<id>
DELETE /api/history/<id>
```

---

## 🤖 ML Models
- `ml_models/mobile_model.pt` → YOLOv8 trained on mobile damage dataset
- `ml_models/laptop_model.pt` → YOLOv8 trained on laptop damage dataset
- Model இல்லன்னா → YOLOv8n pretrained use ஆகும் (placeholder)
