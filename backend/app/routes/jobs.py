import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db

router = APIRouter()


class JobStatusOut(BaseModel):
    document_id: uuid.UUID
    status: str  # pending | processing | ready | failed
    filename: str
    total_pages: int
    chunk_count: int
    error: str | None = None


def _build_status(doc: models.Document, db: Session) -> JobStatusOut:
    count = (
        db.query(func.count(models.Chunk.id))
        .filter(models.Chunk.document_id == doc.id)
        .scalar()
        or 0
    )
    return JobStatusOut(
        document_id=doc.id,
        status=doc.status,
        filename=doc.filename,
        total_pages=doc.total_pages,
        chunk_count=count,
        error=doc.error,
    )


@router.get("/documents/{document_id}/status", response_model=JobStatusOut)
def get_job_status(document_id: uuid.UUID, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _build_status(doc, db)


@router.post("/documents/{document_id}/retry", response_model=JobStatusOut)
def retry_job(document_id: uuid.UUID, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.status == "processing":
        raise HTTPException(status_code=409, detail="Job already processing")
    doc.status = "pending"
    doc.error = None
    db.commit()
    _enqueue(doc.id)
    db.refresh(doc)
    return _build_status(doc, db)


def _enqueue(document_id: uuid.UUID) -> bool:
    """Best-effort enqueue; False when broker is unreachable (dev without redis)."""
    try:
        from ..tasks import process_document

        process_document.delay(str(document_id))
        return True
    except Exception as e:
        print(f"[jobs] enqueue failed (worker will pick up later): {e}")
        return False
