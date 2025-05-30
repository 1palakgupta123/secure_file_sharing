from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from jose import jwt, JWTError
from datetime import datetime, timedelta
import json
import os

from config import SECRET_KEY, ALGORITHM

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
USER_DB_FILE = "users_db.json"


class User(BaseModel):
    email: EmailStr
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USER_DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


@router.post("/signup")
def signup(user: User):
    users = load_users()
    if user.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    users[user.email] = user.dict()
    save_users(users)
    token = create_access_token({"sub": user.email, "role": user.role})
    verify_link = f"http://localhost:8080/auth/verify?token={token}"
    return {"msg": "Signup successful", "verify_url": verify_link}

@router.get("/verify")
def verify_email(token: str):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"msg": "Email verified", "email": payload.get("sub")}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users = load_users()
    user = users.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user["email"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}

# Dependency to get current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    users = load_users()
    if email not in users:
        raise HTTPException(status_code=401, detail="User not found")
    user = users[email]
    user["email"] = email
    return user
