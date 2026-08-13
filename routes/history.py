from flask import Blueprint, request, jsonify
from bson import ObjectId

history_bp = Blueprint("history", __name__)

def serialize(doc):
    """MongoDB ObjectId → string convert"""
    doc["_id"] = str(doc["_id"])
    if "created_at" in doc:
        doc["created_at"] = doc["created_at"].isoformat()
    return doc


@history_bp.route("/history", methods=["GET"])
def get_history():
    """
    GET /api/history?device_type=mobile&limit=10
    
    Response:
    {
        "success": true,
        "total": 10,
        "predictions": [...]
    }
    """
    from app import db

    device_type = request.args.get("device_type", None)
    limit       = request.args.get("limit", 10, type=int)

    query = {}
    if device_type:
        query["device_type"] = device_type.lower()

    records = list(
        db.predictions
        .find(query)
        .sort("created_at", -1)
        .limit(limit)
    )

    return jsonify({
        "success": True,
        "total": len(records),
        "predictions": [serialize(r) for r in records]
    }), 200


@history_bp.route("/history/<prediction_id>", methods=["GET"])
def get_single(prediction_id):
    """
    GET /api/history/<prediction_id>
    Single prediction fetch by MongoDB ID
    """
    from app import db

    try:
        record = db.predictions.find_one({"_id": ObjectId(prediction_id)})
        if not record:
            return jsonify({"success": False, "error": "Not found"}), 404
        return jsonify({"success": True, "prediction": serialize(record)}), 200
    except Exception:
        return jsonify({"success": False, "error": "Invalid prediction ID"}), 400


@history_bp.route("/history/<prediction_id>", methods=["DELETE"])
def delete_prediction(prediction_id):
    """
    DELETE /api/history/<prediction_id>
    """
    from app import db

    try:
        result = db.predictions.delete_one({"_id": ObjectId(prediction_id)})
        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Not found"}), 404
        return jsonify({"success": True, "message": "Deleted ✅"}), 200
    except Exception:
        return jsonify({"success": False, "error": "Invalid prediction ID"}), 400
