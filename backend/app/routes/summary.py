# app/routes/summary.py

import os
from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.services.toc_service import extract_toc_text, detect_mda_page_range
from app.services.mda_extractor import extract_mda_text
from app.services.summarizer import clean_text, textrank_summarize
from app.utils.company_extract import extract_company_name

router = APIRouter()

# Correct shared uploads directory (same as upload.py & analysis.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = Path(os.path.normpath(os.path.join(BASE_DIR, "..", "uploads")))
UPLOAD_DIR.mkdir(exist_ok=True)


@router.get("/{file_id}")
async def get_summary(file_id: str):

    # EXACT SAME LOGIC AS analysis.py + upload.py
    file_path = UPLOAD_DIR / file_id

    if not file_path.exists():
        # Also try matching prefix (uuid_originalname)
        matches = list(UPLOAD_DIR.glob(f"{file_id}*"))
        if not matches:
            raise HTTPException(status_code=404, detail="File not found.")
        file_path = matches[0]

    company = extract_company_name(file_path.name)

    # Step 1 — Extract TOC
    toc_text = extract_toc_text(str(file_path))
    if not toc_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract TOC text.")

    # Step 2 — Detect Page Range
    start_page, end_page = detect_mda_page_range(toc_text)
    if not start_page:
        return {
            "success": False,
            "message": "MDA section not found in TOC",
            "toc_preview": toc_text[:3000],
        }

    # Step 3 — Extract Full MDA Text
    mda_text = extract_mda_text(str(file_path), start_page, end_page)

    # Step 4 — Clean + Summarize
    cleaned = clean_text(mda_text)
    summary = textrank_summarize(cleaned)

    return {
        "success": True,
        "file": file_id,
        "company": company,
        "section": "Management Discussion & Analysis",
        "start_page": start_page,
        "end_page": end_page,
        "extracted_chars": len(mda_text),
        "summary": summary,
        "mda_text": mda_text[:25000],
        "toc_preview": toc_text[:2500]
    }