# Repair App Backend

This is the backend service for the Repair App. The application is built using Flask, MongoDB, and YOLOv8 for device damage detection. It provides APIs for image upload, damage prediction, nearby repair shop search, and prediction history management.

## Features

* Upload device images
* Detect damage using YOLOv8
* Store prediction history in MongoDB
* Find nearby repair shops using Google Places API
* Support for both mobile and laptop devices

## Project Structure

```
repair-app-backend/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
├── routes/
│   ├── upload.py
│   ├── predict.py
│   ├── shops.py
│   └── history.py
├── models/
│   ├── damage_model.py
│   └── db_models.py
├── utils/
│   ├── image_utils.py
│   └── maps_utils.py
└── ml_models/
    ├── mobile_model.pt
    └── laptop_model.pt
```

## Installation

Clone the repository and install the required packages.

```bash
git clone <repository-url>
cd repair-app-backend
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root and add the following values.

```
MONGO_URI=mongodb://localhost:27017/repairapp
GOOGLE_PLACES_API_KEY=your_google_api_key
```

## Running the Application

Start the Flask server using:

```bash
python app.py
```

The server will run on:

```
http://localhost:5000
```

## API Endpoints

### Upload Image

```
POST /api/upload
```

Form Data:

* file
* device_type (mobile or laptop)

### Predict Damage

```
POST /api/predict
```

JSON Request:

```json
{
  "filename": "image.jpg",
  "device_type": "mobile",
  "latitude": 9.9252,
  "longitude": 78.1198
}
```

### Nearby Repair Shops

```
GET /api/shops
```

Query Parameters:

* lat
* lng
* device_type
* radius

### Prediction History

```
GET /api/history
GET /api/history/<id>
DELETE /api/history/<id>
```

## Models

Place the trained YOLOv8 model files inside the `ml_models` directory.

* `mobile_model.pt`
* `laptop_model.pt`

If a trained model is not available, a default YOLOv8 model can be used during development.

## Technology Stack

* Python
* Flask
* MongoDB
* YOLOv8
* Google Places API

## Author

Developed as part of the Repair App project for device damage detection and repair assistance.

