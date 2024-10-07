from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

# Initialize FastAPI
app = FastAPI()

# Mock databases
fake_users_db = {}
fake_shipments_db = []

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

class UserInDB(User):
    hashed_password: str

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
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

# API Endpoints
@app.post("/signup", response_model=User)
async def sign_up(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already registered")
    hashed_password = get_password_hash("password")  # For demo purposes, use "password"
    fake_users_db[user.username] = UserInDB(**user.dict(), hashed_password=hashed_password)
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Create Shipment Endpoint
@app.post("/shipments", response_model=Shipment)
async def create_shipment(shipment: ShipmentCreate, current_user: User = Depends(get_current_user)):
    new_shipment = Shipment(
        id=len(fake_shipments_db) + 1,  # Assign a new ID
        item_name=shipment.item_name,
        quantity=shipment.quantity,
        user_id=current_user.username  # Associate shipment with the logged-in user
    )
    fake_shipments_db.append(new_shipment)
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

# To run the app, use: uvicorn app:app --reload
