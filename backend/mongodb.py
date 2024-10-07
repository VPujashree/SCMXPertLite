from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta, timezone

# Connection string to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['SCMXpertLite']  # Create or connect to the database

# Create collections
users_collection = db['Users']
shipments_collection = db['Shipments']
devices_collection = db['Devices']
sessions_collection = db['Sessions']
roles_collection = db['Roles']
shipment_tracking_logs_collection = db['ShipmentTrackingLogs']
batch_shipments_collection = db['BatchShipments']

# Function to create a user
def create_user(username, email, password_hash, role):
    user = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.now(timezone.utc)  # Use timezone-aware UTC time
    }
    result = users_collection.insert_one(user)
    return str(result.inserted_id)  # Return the new user's ID

# Function to create a device
def create_device(device_id, shipment_id, location, sensor_data):
    device = {
        "device_id": device_id,
        "shipment_id": ObjectId(shipment_id),  # Reference to the shipment
        "location": location,  # Expecting {"latitude": Float, "longitude": Float}
        "sensor_data": sensor_data,  # Expecting {"temperature": Float, "humidity": Float}
        "timestamp": datetime.now(timezone.utc)  # Use timezone-aware UTC time
    }
    result = devices_collection.insert_one(device)
    return str(result.inserted_id)  # Return the new device's ID

# Function to create a shipment
def create_shipment(shipment_number, route_details, device_id, goods_type, expected_delivery_date):
    shipment = {
        "shipment_number": shipment_number,
        "route_details": route_details,  # Expected to be a dictionary
        "device": ObjectId(device_id) if device_id else None,  # Convert string ID to ObjectId or set to None
        "PO_number": "PO987654",
        "NDC_number": "001234567890",
        "goods_serial_number": "GSN-0001",
        "container_number": "CNT12345",
        "goods_type": goods_type,
        "expected_delivery_date": expected_delivery_date,
        "shipment_desc": "Electronic shipment",
        "created_at": datetime.now(timezone.utc),  # Use timezone-aware UTC time
        "updated_at": datetime.now(timezone.utc)   # Use timezone-aware UTC time
    }
    result = shipments_collection.insert_one(shipment)
    return str(result.inserted_id)  # Return the new shipment's ID

# Function to create a session
def create_session(user_id, jwt_token):
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)  # Expires in 1 hour
    session = {
        "user_id": ObjectId(user_id),  # Reference to User ID
        "jwt_token": jwt_token,
        "expires_at": expires_at
    }
    result = sessions_collection.insert_one(session)
    return str(result.inserted_id)  # Return the new session's ID

# Function to create a role
def create_role(role, permissions):
    role_doc = {
        "role": role,
        "permissions": permissions
    }
    result = roles_collection.insert_one(role_doc)
    return str(result.inserted_id)  # Return the new role's ID

# Function to log shipment tracking
def log_shipment_tracking(shipment_id, status, location):
    log = {
        "shipment_id": ObjectId(shipment_id),  # Reference to Shipment ID
        "status": status,
        "location": location,  # Expecting {"latitude": Float, "longitude": Float}
        "timestamp": datetime.now(timezone.utc)  # Use timezone-aware UTC time
    }
    result = shipment_tracking_logs_collection.insert_one(log)
    return str(result.inserted_id)  # Return the new log's ID

# Function to create a batch shipment
def create_batch_shipment(batch_id, shipment_ids):
    batch = {
        "batch_id": batch_id,
        "shipment_ids": [ObjectId(id) for id in shipment_ids],  # Convert string IDs to ObjectIds
        "created_at": datetime.now(timezone.utc)  # Use timezone-aware UTC time
    }
    result = batch_shipments_collection.insert_one(batch)
    return str(result.inserted_id)  # Return the new batch's ID

# Example Usage
if __name__ == "__main__":
    # Create roles
    admin_role_id = create_role("Admin", ["create", "read", "update", "delete"])
    user_role_id = create_role("User", ["read"])

    # Create a user
    user_id = create_user("john_doe", "john@example.com", "hashed_password", "User")
    print(f"User created with ID: {user_id}")

    # Create a shipment
    shipment_id = create_shipment("SHIP1234", {"from": "New York", "to": "San Francisco"}, None, "Perishable", datetime(2024, 10, 15))
    print(f"Shipment created with ID: {shipment_id}")

    # Create a device
    device_id = create_device("DEV001", shipment_id, {"latitude": 37.7749, "longitude": -122.4194}, {"temperature": 20.5, "humidity": 60})
    print(f"Device created with ID: {device_id}")

    # Create a session
    jwt_token = "generated_jwt_token_here"
    session_id = create_session(user_id, jwt_token)
    print(f"Session created with ID: {session_id}")

    # Log shipment tracking
    tracking_log_id = log_shipment_tracking(shipment_id, "In Transit", {"latitude": 40.7128, "longitude": -74.0060})
    print(f"Tracking log created with ID: {tracking_log_id}")

    # Create a batch shipment
    batch_id = create_batch_shipment("BATCH001", [shipment_id])
    print(f"Batch shipment created with ID: {batch_id}")
