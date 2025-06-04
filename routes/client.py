
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from jose import jwt, JWTError
from datetime import timedelta, datetime
import os
import json

from routes.auth import get_current_user
from config import SECRET_KEY, ALGORITHM

router = APIRouter()
DB_FILE = "files_db.json"

# Load metadata from disk
def load_files_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

# Generate a secure download link
@router.get("/download/{file_id}")
def generate_download_link(file_id: str, user=Depends(get_current_user)):
    files_db = load_files_db()
    
    if user["role"] != "client":
        raise HTTPException(status_code=403, detail="Only clients can download files.")
    if file_id not in files_db:
        raise HTTPException(status_code=404, detail="File not found")

    expire = datetime.utcnow() + timedelta(minutes=30)
    token_data = {
        "sub": user["email"],
        "file_id": file_id,
        "role": user["role"],
        "exp": expire
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {"download_link": f"/client/download-secure/{token}"}

# Allow file download using secure token — no login required
@router.get("/download-secure/{token}")
def secure_download(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        file_id = payload.get("file_id")
        token_role = payload.get("role")

        if token_role != "client":
            raise HTTPException(status_code=403, detail="Unauthorized role")

        files_db = load_files_db()
        if file_id not in files_db:
            raise HTTPException(status_code=404, detail="File not found")

        file_meta = files_db[file_id]
        return FileResponse(
            path=file_meta["path"],
            filename=file_meta["filename"],
            media_type="application/octet-stream"
        )
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

# List files for logged-in client users
@router.get("/files")
def list_files(user=Depends(get_current_user)):
    if user["role"] != "client":
        raise HTTPException(status_code=403, detail="Not authorized")

    files_db = load_files_db()
    return {"files": [{"id": fid, "filename": f["filename"]} for fid, f in files_db.items()]}
