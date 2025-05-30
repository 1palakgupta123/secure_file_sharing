from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import uuid, os, shutil
from routes.auth import get_current_user
from database import files_db
from config import UPLOAD_DIR

router = APIRouter()
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    if user["role"] != "ops":
        raise HTTPException(status_code=403, detail="Only ops users can upload files")
    
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    files_db[file_id] = {
        "filename": file.filename,
        "path": file_path,
        "uploader": user["email"]
    }

    return {"msg": "File uploaded successfully", "file_id": file_id}    