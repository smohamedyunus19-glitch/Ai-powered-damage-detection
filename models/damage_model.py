from ultralytics import YOLO
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODELS = {
    'mobile': os.path.join(BASE_DIR, 'ml_models', 'mobile_model.pt'),
    'laptop': os.path.join(BASE_DIR, 'ml_models', 'laptop_model.pt'),
}

loaded_models = {}

def get_model(device_type):
    if device_type not in loaded_models:
        model_path = MODELS.get(device_type)
        if model_path and os.path.exists(model_path):
            loaded_models[device_type] = YOLO(model_path)
    return loaded_models.get(device_type)

def predict_damage(image_path, device_type):
    model = get_model(device_type)
    if not model:
        return {'damage_type': 'unknown', 'confidence': 0.0, 'severity': 'low', 'all_detections': []}
    
    results = model(image_path)
    detections = []
    
    for r in results:
        for box in r.boxes:
            detections.append({
                'class': r.names[int(box.cls)],
                'confidence': float(box.conf)
            })
    
    if detections:
        best = max(detections, key=lambda x: x['confidence'])
        confidence = best['confidence']
        severity = 'high' if confidence > 0.7 else 'medium' if confidence > 0.4 else 'low'
        return {
            'damage_type': best['class'],
            'confidence': confidence,
            'severity': severity,
            'all_detections': detections
        }
    
    return {'damage_type': 'no_damage', 'confidence': 0.0, 'severity': 'low', 'all_detections': []}