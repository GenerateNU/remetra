import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from database import get_db
from services.ingest_service import IngestService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["Ingest"])

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


@router.post("/pdf", status_code=status.HTTP_201_CREATED)
async def ingest_pdf_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Ingest a single uploaded PDF into the knowledge base."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted.",
        )

    ingest_service = IngestService()
    try:
        result = ingest_service.ingest_pdf_file(db, file.file, source=file.filename)
    except Exception as e:
        logger.error("Failed to ingest '%s': %s", file.filename, e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not process PDF: {e}",
        )
    return result


@router.post("/folder", status_code=status.HTTP_201_CREATED)
async def ingest_folder_endpoint(db: Session = Depends(get_db)):
    """Seed the knowledge base from all PDFs in backend/data/raw/. Idempotent."""
    if not RAW_DATA_DIR.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Raw data directory not found: {RAW_DATA_DIR}",
        )

    if not any(RAW_DATA_DIR.glob("*.pdf")):
        return {"message": "No PDF files found in data/raw/", "sources_ingested": []}

    ingest_service = IngestService()
    try:
        result = ingest_service.ingest_folder(db)
    except Exception as e:
        logger.error("Failed to ingest folder: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Folder ingest failed: {e}",
        )
    return result
