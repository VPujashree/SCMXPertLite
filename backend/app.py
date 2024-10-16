from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, ValidationError  # Import ValidationError
from typing import List, Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from urllib.parse import quote_plus


# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5501"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# URL encode the username and password
username = quote_plus("Admin")
password = quote_plus("admin@123")

# Update the MongoDB connection string
MONGO_DETAILS = f"mongodb+srv://{username}:{password}@scmxpertlite.3ukab.mongodb.net/?retryWrites=true&w=majority&appName=SCMXPertLite"

client = AsyncIOMotorClient(MONGO_DETAILS)
db = client['SCMXPertLite']  # Replace with your database name

# JWT Configuration
SECRET_KEY = "910e0cf7760ccf7d08a228a06b0cc2f43687e94f5a6e9c0b3a2faeb8bb59f4c8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User Models
class User(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    role: str  # Added role field

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None  # Optional field
    role: str  # Assuming role is a required field
    disabled: Optional[bool] = None  # Optional field

class UserInDB(User):
    hashed_password: str

# Shipment Models
class ShipmentCreate(BaseModel):  # Create a separate model for request
    item_name: str
    quantity: int
    description: str  # Include description
    status: str       # Include status
    created_at: datetime  # Include created_at

class Shipment(ShipmentCreate):  # Inherit from ShipmentCreate for the response
    id: str  # MongoDB generates ObjectId, change to str
    user_id: str  # Associate shipment with user

class ResetPassword(BaseModel):
    email: EmailStr
    new_password: str

# Password and JWT Utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user(username: str):
    user_data = await db["users"].find_one({"username": username})
    if user_data:
        return UserInDB(**user_data)  # This should properly instantiate UserInDB if user_data is not None
    return None  # Explicitly return None if user not found

async def get_current_user(token: str = Depends(oauth2_scheme)):
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

    user = await get_user(username)
    if user is None:
        raise credentials_exception
    return user

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open(os.path.join("frontend/static", "index.html")) as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/signup", response_model=User)
async def sign_up(user: UserCreate):
    logging.info("Attempting to sign up user: %s", user.username)
    try:
        # Check if username already exists
        existing_user = await db["users"].find_one({"username": user.username})
        if existing_user:
            logging.warning("User already registered: %s", user.username)
            raise HTTPException(status_code=400, detail="User already registered")

        # Hash the password
        hashed_password = get_password_hash(user.password)

        # Prepare user data to insert into the database
        user_dict = user.dict(exclude={"password"})  # Exclude password for storage
        user_dict['hashed_password'] = hashed_password  # Add hashed password to user dict

        # Insert user into MongoDB
        await db["users"].insert_one(user_dict)
        logging.info("User registered successfully: %s", user.username)

        return User(**user_dict)  # Return User instance
    except ValidationError as e:
        logging.error("Validation error: %s", e)
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        logging.error("Error during signup: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logging.warning("Incorrect username or password for user: %s", form_data.username)
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    
    logging.info("User logged in successfully: %s", user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/shipments", response_model=Shipment)
async def create_shipment(shipment: ShipmentCreate, current_user: User = Depends(get_current_user)):
    new_shipment = Shipment(
        id=str(ObjectId()),  # Generate a new ObjectId for the shipment
        item_name=shipment.item_name,
        quantity=shipment.quantity,
        user_id=current_user.username,
        description=shipment.description,  # Include description
        status=shipment.status,              # Include status
        created_at=datetime.utcnow()          # Include created_at
    )
    
    # Insert the new shipment into MongoDB
    result = await db["shipments"].insert_one(new_shipment.dict(exclude={"id"}))

    # Fetch the created shipment from MongoDB and convert _id to string
    created_shipment = await db["shipments"].find_one({"_id": result.inserted_id})
    
    # Create a new Shipment instance with the data from created_shipment
    return Shipment(
        id=str(created_shipment["_id"]),  # Convert ObjectId to string
        item_name=created_shipment["item_name"],
        quantity=created_shipment["quantity"],
        user_id=created_shipment["user_id"],
        description=created_shipment["description"],  # Add description
        status=created_shipment["status"],              # Add status
        created_at=created_shipment["created_at"]       # Add created_at
    )

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

@app.post("/reset-password")
async def reset_password(reset_data: ResetPassword):
    user = await db["users"].find_one({"email": reset_data.email})
    if not user:
        logging.warning("User not found for password reset: %s", reset_data.email)
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = get_password_hash(reset_data.new_password)
    
    # Update the user's password in the database
    await db["users"].update_one({"email": reset_data.email}, {"$set": {"hashed_password": hashed_password}})
    logging.info("Password updated successfully for user: %s", reset_data.email)
    return {"msg": "Password updated successfully"}

# cd SCMXPertLite/backend
# uvicorn app:app --reload