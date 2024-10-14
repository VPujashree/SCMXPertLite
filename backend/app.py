from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import List
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pymongo import MongoClient
import os
import secrets

# MongoDB Configuration
MONGO_DETAILS = "mongodb://localhost:27017"  # Replace with your MongoDB connection string
client = MongoClient(MONGO_DETAILS)
database = client['SCMXPertLite']  # Replace with your database name
users_collection = database['users']  # Your users collection
shipments_collection = database['shipments']  # Your shipments collection

# Initialize FastAPI
app = FastAPI()

# Mount the static directory with absolute path
app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "frontend/static")), name="static")

# Serve index.html from the frontend directory
@app.get("/")
def read_root():
    return FileResponse(os.path.join(os.getcwd(), "frontend/static/index.html"))

# JWT Configuration
SECRET_KEY = "910e0cf7760ccf7d08a228a06b0cc2f43687e94f5a6e9c0b3a2faeb8bb59f4c8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User Models
class User(BaseModel):
    username: str
    email: EmailStr
    full_name: str = None
    disabled: bool = None
    role: str  # Added role field
    password: str  # Added password field

class UserInDB(User):
    hashed_password: str  # This field is only for the database representation

# Shipment Models
class ShipmentCreate(BaseModel):  # Create a separate model for request
    item_name: str
    quantity: int

class Shipment(ShipmentCreate):  # Inherit from ShipmentCreate for the response
    id: int
    user_id: str  # Associate shipment with user

# Password and JWT Utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = users_collection.find_one({"username": username})  # Query from MongoDB
    if user is None:
        raise credentials_exception
    # Create a UserInDB object with the required fields
    return UserInDB(
        username=user['username'],
        email=user['email'],
        full_name=user.get('full_name', None),
        disabled=user.get('disabled', None),
        role=user.get('role', None),
        hashed_password=user['hashed_password']  # Include hashed password
    )

# API Endpoints
@app.post("/signup", response_model=User)
async def sign_up(user: User):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="User already registered")
    hashed_password = get_password_hash(user.password)  # Ensure you hash the password
    user_dict = user.dict()
    user_dict['hashed_password'] = hashed_password
    users_collection.insert_one(user_dict)  # Insert into MongoDB
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"username": form_data.username})  # Fetch from MongoDB
    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user['username']}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Create Shipment Endpoint
@app.post("/shipments", response_model=Shipment)
async def create_shipment(shipment: ShipmentCreate, current_user: User = Depends(get_current_user)):
    new_shipment = {
        "_id": shipments_collection.count_documents({}) + 1,  # Incremental ID
        "item_name": shipment.item_name,
        "quantity": shipment.quantity,
        "user_id": current_user.username
    }
    shipments_collection.insert_one(new_shipment)  # Insert into MongoDB
    return new_shipment

# Role-based access control
def role_required(role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_checker

@app.get("/admin")
async def admin_route(current_user: User = Depends(role_required("admin"))):
    return {"msg": "Welcome Admin!"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Password Reset Endpoint
class PasswordResetRequest(BaseModel):
    username: str
    email: EmailStr

def generate_secure_password():
    return secrets.token_urlsafe(16)  # Generates a secure random password

@app.post("/reset-password")
async def reset_password(request: PasswordResetRequest):
    user = users_collection.find_one({"username": request.username, "email": request.email})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate a new secure password
    new_password = generate_secure_password()
    hashed_password = get_password_hash(new_password)

    # Update the password in the database
    users_collection.update_one({"_id": user["_id"]}, {"$set": {"hashed_password": hashed_password}})
    
    # Send the new password to the user's email (implement this function)
    # send_password_email(request.email, new_password)  # Placeholder for email sending logic

    return {"msg": "Password reset successful. New password sent to your email."}

# To run the app, use: uvicorn backend.app:app --reload
