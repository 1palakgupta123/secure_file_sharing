from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import User, Token
from database import users_db
from utils import create_access_token, verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter()

@router.post("/signup")
def signup(user: User):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Save user with password key (no hashing for now)
    users_db[user.email] = user.dict()
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
    user = users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token({"sub": user["email"], "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    if email not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    user = users_db[email]
    user["email"] = email  
    return user
