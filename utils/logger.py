from datetime import datetime
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.face_auth_db
logs = db.logs

def log_access(user_id):
    logs.insert_one({
        "user_id": user_id,
        "timestamp": datetime.now(),
        "confidence": "pass"
    })