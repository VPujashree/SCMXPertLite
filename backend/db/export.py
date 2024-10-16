# code to export the schema and stored in .xls form in downloads folder
import pandas as pd
from pymongo import MongoClient
import os

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['SCMXpertLite']

# Define a function to retrieve collection schemas
def get_collection_schema(collection_name):
    schema = {
        "Field Name": [],
        "Data Type": [],
        "Description": [],
        "Key": [],
        "Constraints/Validation": []
    }

    if collection_name == 'Users':
        schema["Field Name"] = ['_id', 'username', 'email', 'password_hash', 'role', 'created_at']
        schema["Data Type"] = ['ObjectId', 'String', 'String', 'String', 'String', 'DateTime']
        schema["Description"] = [
            'Unique identifier for each user',
            'Username of the user',
            'Email of the user',
            'Hashed password for security',
            'Role of the user (Admin, User)',
            'Date when the user was created'
        ]
        schema["Key"] = ['Primary Key', '', '', '', '', '']
        schema["Constraints/Validation"] = ['Auto-generated', 'Required, Unique', 'Required, Unique', 'Required', 'Enum: ["Admin", "User"]', 'Auto-generated']

    elif collection_name == 'Shipments':
        schema["Field Name"] = [
            '_id', 
            'shipment_number', 
            'route_details', 
            'device', 
            'PO_number', 
            'NDC_number', 
            'goods_serial_number', 
            'container_number', 
            'goods_type', 
            'expected_delivery_date', 
            'shipment_desc', 
            'created_at', 
            'updated_at'
        ]
    
        schema["Data Type"] = [
            'ObjectId', 
            'String', 
            'Object', 
            'ObjectId', 
            'String', 
            'String', 
            'String', 
            'String', 
            'String', 
            'DateTime', 
            'String', 
            'DateTime', 
            'DateTime'
        ]
    
        schema["Description"] = [
            'Unique identifier for each shipment',
            'Shipment identifier (unique)',
            'Embedded document for route info',
            'Reference to device used for shipment',
            'Purchase Order number for the shipment',
            'National Drug Code number for the goods',
            'Serial number of goods in the shipment',
            'Shipping container identifier',
            'Type of goods (e.g., Perishable, Non-Perishable)',
            'Expected delivery date',
            'Description of the shipment',
            'Date when the shipment was created',
            'Date when the shipment was last updated'
        ]
    
        schema["Key"] = [
            'Primary Key', 
            '', 
            '', 
            'Foreign Key', 
            '', 
            '', 
            'Optional, Unique', 
            'Optional, Unique', 
            '', 
            'Required', 
            '', 
            '', 
            'Auto-generated'
        ]
    
        schema["Constraints/Validation"] = [
            'Auto-generated', 
            'Required, Unique', 
            '', 
            '', 
            'Optional', 
            'Optional', 
            'Optional, Unique', 
            'Optional, Unique', 
            'Enum: ["Perishable", "Non-Perishable"]', 
            'Required', 
            'Optional', 
            'Auto-generated', 
            'Auto-generated'
        ]

    elif collection_name == 'Devices':
        schema["Field Name"] = ['_id', 'device_id', 'shipment_id', 'location', 'sensor_data', 'timestamp']
        schema["Data Type"] = ['ObjectId', 'String', 'ObjectId', 'Object', 'Object', 'DateTime']
        schema["Description"] = [
            'Unique identifier for each device',
            'Device identifier',
            'Reference to shipment being tracked',
            'Location coordinates (latitude/longitude)',
            'Sensor data readings (e.g., temperature, humidity)',
            'Time when the data was recorded'
        ]
        schema["Key"] = ['Primary Key', '', 'Foreign Key', '', '', '']
        schema["Constraints/Validation"] = ['Auto-generated', 'Required, Unique', 'Links to Shipments collection', '', '', 'Auto-generated']

    elif collection_name == 'Sessions':
        schema["Field Name"] = ['_id', 'user_id', 'jwt_token', 'expires_at']
        schema["Data Type"] = ['ObjectId', 'ObjectId', 'String', 'DateTime']
        schema["Description"] = [
            'Unique identifier for each session',
            'Reference to the authenticated user',
            'JWT session token',
            'Expiration time of the session'
        ]
        schema["Key"] = ['Primary Key', 'Foreign Key', '', '']
        schema["Constraints/Validation"] = ['Auto-generated', 'Links to Users collection', 'Required', 'Auto-generated, Required']

    elif collection_name == 'Roles':
        schema["Field Name"] = ['_id', 'role', 'permissions']
        schema["Data Type"] = ['ObjectId', 'String', 'Array']
        schema["Description"] = [
            'Unique identifier for each role',
            'Name of the role (e.g., Admin, User)',
            'List of permissions assigned to the role'
        ]
        schema["Key"] = ['Primary Key', '', '']
        schema["Constraints/Validation"] = ['Auto-generated', 'Required, Unique', 'Array of strings']

    elif collection_name == 'ShipmentTrackingLogs':
        schema["Field Name"] = ['_id', 'shipment_id', 'status', 'location', 'timestamp']
        schema["Data Type"] = ['ObjectId', 'ObjectId', 'String', 'Object', 'DateTime']
        schema["Description"] = [
            'Unique identifier for each tracking log',
            'Reference to the tracked shipment',
            'Current status of the shipment',
            'Location coordinates at the time of logging',
            'Time when the status was recorded'
        ]
        schema["Key"] = ['Primary Key', 'Foreign Key', '', '', '']
        schema["Constraints/Validation"] = ['Auto-generated', 'Links to Shipments collection', '', '', 'Auto-generated']

    elif collection_name == 'BatchShipments':
        schema["Field Name"] = ['_id', 'batch_id', 'shipment_ids', 'created_at']
        schema["Data Type"] = ['ObjectId', 'String', 'Array', 'DateTime']
        schema["Description"] = [
            'Unique identifier for each batch shipment',
            'Batch identifier',
            'List of shipment IDs in the batch',
            'Date when the batch was created'
        ]
        schema["Key"] = ['Primary Key', '', '', '']
        schema["Constraints/Validation"] = ['Auto-generated', 'Required, Unique', 'Array of ObjectIds', 'Auto-generated']

    # Check if all lists are the same length
    lengths = {len(v) for v in schema.values()}
    print(f"Lengths for {collection_name}: {[len(v) for v in schema.values()]}")
    if len(lengths) > 1:
        raise ValueError(f"Inconsistent lengths in schema for collection '{collection_name}'.")

    return pd.DataFrame(schema)

# Create a list of collection names
collection_names = ['Users', 'Shipments', 'Devices', 'Sessions', 'Roles', 'ShipmentTrackingLogs', 'BatchShipments']

# Path to save the Excel file in Downloads folder
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
file_path = os.path.join(downloads_folder, 'SCMXpertLite_Schema_and_Data.xlsx')

# Initialize an Excel writer
with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    for collection in collection_names:
        # Export schema
        schema_df = get_collection_schema(collection)
        schema_df.to_excel(writer, sheet_name=f"{collection}_Schema", index=False)

        # Export data
        data_df = pd.DataFrame(list(db[collection].find({})))  # Fetch all data from the collection
        if not data_df.empty:  # Check if the collection has data
            data_df.to_excel(writer, sheet_name=f"{collection}_Data", index=False)

print(f"Schema and data exported to {file_path}")
