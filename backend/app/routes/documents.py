import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import settings
from ..db import get_db

router = APIRouter()


def _ensure_upload_dir() -> None:
    os.makedirs(settings.upload_dir, exist_ok=True)


@router.post("/documents/upload", response_model=schemas.UploadResponse)
def upload_document(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are accepted")

    _ensure_upload_dir()
    doc_id = uuid.uuid4()
    stored_path = os.path.join(settings.upload_dir, f"{doc_id}.pdf")

    size_bytes = 0
    with open(stored_path, "wb") as out:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            size_bytes += len(chunk)
            out.write(chunk)

    max_bytes = settings.max_upload_mb * 1024 * 1024
    if size_bytes > max_bytes:
        os.remove(stored_path)
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.max_upload_mb} MB limit",
        )

    doc = models.Document(
        id=doc_id,
        filename=file.filename,
        stored_path=stored_path,
        file_size_bytes=size_bytes,
        total_pages=0,  # Phase 2: filled by Celery ingestion worker
        status="pending",  # Phase 2: pending -> processing -> ready
    )
    db.add(doc)
    db.commit()

    from .jobs import _enqueue

    queued = _enqueue(doc.id)

    return schemas.UploadResponse(
        document_id=doc.id,
        filename=doc.filename,
        status=doc.status,
        message="Upload accepted. Ingestion worker (Phase 2) will process it."
        if queued
        else "Upload stored. Worker offline — retry via POST /documents/{id}/retry.",
    )


@router.get("/documents", response_model=list[schemas.DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(models.Document).order_by(models.Document.created_at.desc()).all()
    out = []
    for d in docs:
        count = (
            db.query(func.count(models.Chunk.id))
            .filter(models.Chunk.document_id == d.id)
            .scalar()
            or 0
        )
        out.append(
            schemas.DocumentOut(
                id=d.id,
                filename=d.filename,
                file_size_bytes=d.file_size_bytes,
                total_pages=d.total_pages,
                status=d.status,
                error=d.error,
                created_at=d.created_at,
                chunk_count=count,
            )
        )
    return out


@router.get("/documents/{document_id}", response_model=schemas.DocumentOut)
def get_document(document_id: uuid.UUID, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    count = (
        db.query(func.count(models.Chunk.id))
        .filter(models.Chunk.document_id == doc.id)
        .scalar()
        or 0
    )
    return schemas.DocumentOut(
        id=doc.id,
        filename=doc.filename,
        file_size_bytes=doc.file_size_bytes,
        total_pages=doc.total_pages,
        status=doc.status,
        error=doc.error,
        created_at=doc.created_at,
        chunk_count=count,
    )
