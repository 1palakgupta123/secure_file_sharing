from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import uuid, os, shutil
from routes.auth import get_current_user
from database import files_db
from config import UPLOAD_DIR

router = APIRouter()
os.makedirs(UPLOAD_DIR, exist_ok=True)

import json

router = APIRouter()
UPLOAD_DIR = "uploads"
DB_FILE = "files_db.json"

# Load or initialize files_db
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        files_db = json.load(f)
else:
    files_db = {}

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        files_db[file_id] = {
            "filename": file.filename,
            "path": file_path
        }

        # Save metadata permanently to file
        with open(DB_FILE, "w") as f:
            json.dump(files_db, f)

        return {"file_id": file_id, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"msg": "File uploaded successfully", "file_id": file_id}    
