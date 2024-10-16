# code to create dummy values into mongodb
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import pymongo
from urllib.parse import quote_plus

# URL encode the username and password
username = quote_plus("Admin")
password = quote_plus("admin@123")

# Update the MongoDB connection string
MONGO_DETAILS = f"mongodb+srv://{username}:{password}@scmxpertlite.3ukab.mongodb.net/?retryWrites=true&w=majority&appName=SCMXPertLite"

client = MongoClient(MONGO_DETAILS)
db = client['SCMXPertLite']  # Replace with your database name

# Users Collection
users_collection = db['users']
roles_collection = db['roles']
shipments_collection = db['shipments']
devices_collection = db['devices']
sessions_collection = db['sessions']
tracking_logs_collection = db['shipment_tracking_logs']
batch_shipments_collection = db['batch_shipments']

# Create dummy data for roles
role_admin = roles_collection.insert_one({
    "role": "admin",
    "permissions": ["manage_users", "view_shipments", "manage_roles"]
})
role_user = roles_collection.insert_one({
    "role": "user",
    "permissions": ["view_own_shipments"]
})

# Create dummy users
user1 = users_collection.insert_one({
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "disabled": False,
    "role": role_user.inserted_id,  # Foreign key to roles collection
    "hashed_password": "hashed_password_123",
    "created_at": datetime.utcnow()
})

user2 = users_collection.insert_one({
    "username": "admin_user",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "disabled": False,
    "role": role_admin.inserted_id,  # Foreign key to roles collection
    "hashed_password": "hashed_password_admin",
    "created_at": datetime.utcnow()
})

# Create dummy shipments
shipment1 = shipments_collection.insert_one({
    "shipment_number": "SHIP123456",
    "route_details": {"origin": "New York", "destination": "Los Angeles"},
    "device": None,  # To be linked with device data later
    "PO_number": "PO123456",
    "NDC_number": "NDC12345",
    "goods_serial_number": "GSN1234567",
    "container_number": "CNT1234567",
    "goods_type": "electronics",  # Enum type: Can be 'electronics', 'food', etc.
    "expected_delivery_date": datetime.utcnow() + timedelta(days=10),
    "shipment_desc": "Electronics shipment",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
})

# Create dummy devices
device1 = devices_collection.insert_one({
    "device_id": "DEV123456",
    "shipment_id": shipment1.inserted_id,  # Foreign key to shipments collection
    "location": {"latitude": 40.7128, "longitude": -74.0060},
    "sensor_data": {"temperature": 22.5, "humidity": 55},
    "timestamp": datetime.utcnow()
})

# Update the shipment to link the device
shipments_collection.update_one({"_id": shipment1.inserted_id}, {"$set": {"device": device1.inserted_id}})

# Create dummy sessions
session1 = sessions_collection.insert_one({
    "user_id": user1.inserted_id,  # Foreign key to users collection
    "jwt_token": "dummy_jwt_token_123",
    "expires_at": datetime.utcnow() + timedelta(hours=1)
})

# Create dummy tracking logs
tracking_log1 = tracking_logs_collection.insert_one({
    "shipment_id": shipment1.inserted_id,  # Foreign key to shipments collection
    "status": "In Transit",
    "location": {"latitude": 35.6895, "longitude": 139.6917},
    "timestamp": datetime.utcnow()
})

# Create dummy batch shipment
batch_shipment1 = batch_shipments_collection.insert_one({
    "batch_id": "BATCH123456",
    "shipment_ids": [shipment1.inserted_id],  # Array of shipment IDs
    "created_at": datetime.utcnow()
})

# Print inserted IDs for reference
print(f"Inserted role (admin): {role_admin.inserted_id}")
print(f"Inserted role (user): {role_user.inserted_id}")
print(f"Inserted user 1: {user1.inserted_id}")
print(f"Inserted user 2: {user2.inserted_id}")
print(f"Inserted shipment 1: {shipment1.inserted_id}")
print(f"Inserted device 1: {device1.inserted_id}")
print(f"Inserted session 1: {session1.inserted_id}")
print(f"Inserted tracking log 1: {tracking_log1.inserted_id}")
print(f"Inserted batch shipment 1: {batch_shipment1.inserted_id}")

# cd SCMXPertLite/backend/db
# python mongo_script.py
