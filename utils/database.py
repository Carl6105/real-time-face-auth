import bcrypt
import face_recognition
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client.face_auth_db
users = db.users
logs = db.logs

# Static admin credentials
ADMIN_NAME = "Admin"
ADMIN_PASSWORD = "Password"
ADMIN_HASH = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()

# Ensure admin exists only once
def ensure_admin():
    if not users.find_one({"name": ADMIN_NAME}):
        users.insert_one({
            "name": ADMIN_NAME,
            "face_encoding": [],
            "is_admin": True,
            "password_hash": ADMIN_HASH,
            "last_login": None
        })

# Call on app load to ensure admin
ensure_admin()

def register_user(name, encoding, is_admin=False):
    if name == ADMIN_NAME:
        return  # prevent admin override
    users.insert_one({
        "name": name,
        "face_encoding": encoding,
        "is_admin": is_admin,
        "last_login": None
    })

def get_user_by_encoding(input_encoding):
    all_users = list(users.find())
    for user in all_users:
        if user['face_encoding']:
            match = face_recognition.compare_faces([user['face_encoding']], input_encoding)
            if match[0]:
                return user
    return None

def update_last_login(user_id):
    users.update_one({"_id": user_id}, {"$set": {"last_login": datetime.now()}})

def update_face_encoding(user_id, new_encoding):
    users.update_one({"_id": user_id}, {"$set": {"face_encoding": new_encoding}})

def is_user_admin(user):
    return user.get("is_admin", False)

def verify_admin_password(user, input_password):
    return bcrypt.checkpw(input_password.encode(), user['password_hash'].encode())

def get_login_logs(user_id):
    return list(logs.find({"user_id": user_id}))

def get_all_users():
    return list(users.find())

def delete_user(user_id):
    db.users.delete_one({"_id": user_id})
    db.logs.delete_many({"user_id": user_id})