# import os
# import uuid
# from fastapi import APIRouter, UploadFile, File, HTTPException, status

# from app.utils.company_extract import extract_company_name

# router = APIRouter()

# UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# @router.post("/", status_code=201)
# async def upload_file(file: UploadFile = File(...)):
#     """
#     Upload a financial document (PDF, image, Excel, etc.).
#     """
#     if not file:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded.")
#     filename = file.filename
#     if not filename:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must have a filename.")
#     ext = os.path.splitext(filename)[1].lower()
#     allowed_exts = {".pdf", ".jpg", ".jpeg", ".png", ".xlsx", ".xls", ".txt"}
#     if ext not in allowed_exts:
#         raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f"Unsupported file type: {ext}")

#     # Save file with a unique name to avoid collisions
#     unique_name = f"{uuid.uuid4().hex}_{filename}"
#     file_path = os.path.join(UPLOAD_DIR, unique_name)
#     try:
#         with open(file_path, "wb") as buffer:
#             content = await file.read()
#             buffer.write(content)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not save file: {e}")

#     detected_company = extract_company_name(filename)

#     return {
#         "message": "File uploaded successfully.",
#         "file_id": unique_name,
#         "stored_as": unique_name,
#         "file_path": file_path,
#         "company": detected_company,
#     }


# app/routes/upload.py
import os
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.utils.company_extract import extract_company_name

router = APIRouter()
logger = logging.getLogger("app.routes.upload")

# Shared absolute uploads directory (same logic as analysis)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", status_code=201)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a financial document and return the stored file id.
    Stored filename format: <uuid>_<original_filename>
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    original_name = file.filename or ""
    ext = os.path.splitext(original_name)[1].lower()
    allowed_exts = {".pdf", ".jpg", ".jpeg", ".png", ".xlsx", ".xls", ".txt"}
    if ext not in allowed_exts:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {ext}")

    unique_name = f"{uuid.uuid4().hex}_{original_name}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info("Saved upload: %s", file_path)
    except Exception as e:
        logger.exception("Failed to save uploaded file")
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    detected_company = extract_company_name(original_name)

    return {
        "message": "File uploaded successfully.",
        "file_id": unique_name,
        "stored_as": unique_name,
        "file_path": file_path,
        "company": detected_company,
    }