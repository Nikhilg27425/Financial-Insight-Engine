from fastapi import APIRouter, HTTPException, status
from pathlib import Path
from app.services.ocr_service import extract_text

router = APIRouter()

UPLOAD_DIR = Path("uploads")  # same upload directory

@router.get("/{file_id}", tags=["Analysis"])
async def extract_text_endpoint(file_id: str):
    """
    Extract text from an already uploaded file.
    """
    file_path = UPLOAD_DIR / f"{file_id}.pdf"  # assuming all files are PDF
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found."
        )

    try:
        extracted_text = extract_text(str(file_path))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text extraction failed: {type(e).__name__}"
        )

    return {"file_id": file_id, "extracted_text": extracted_text[:10000]}