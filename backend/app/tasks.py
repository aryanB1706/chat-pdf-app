"""Async ingestion: parse PDF -> chunk -> embed -> store in pgvector.

Automatic retries on any exception (3 attempts, exponential backoff).
Tracks status on documents: pending -> processing -> ready | failed.
"""

import uuid

from sqlalchemy import delete

from . import models
from .config import settings
from .db import SessionLocal
from .embeddings import embed_texts
from .pdf import chunk_pages, extract_pages
from .worker import celery_app


@celery_app.task(
    bind=True,
    name="ingest_document",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
    retry_backoff=True,
)
def process_document(self, document_id: str) -> dict:
    db = SessionLocal()
    try:
        doc = (
            db.query(models.Document)
            .filter(models.Document.id == uuid.UUID(document_id))
            .first()
        )
        if not doc:
            return {"ok": False, "error": "document not found"}

        doc.status = "processing"
        doc.error = None
        db.commit()

        pages = extract_pages(doc.stored_path)
        chunks = chunk_pages(pages)

        # Replace any previous chunks (idempotent re-ingest / retry).
        db.execute(
            delete(models.Chunk).where(models.Chunk.document_id == doc.id)
        )

        batch = settings.embedding_batch_size
        rows: list[models.Chunk] = []
        for i in range(0, len(chunks), batch):
            batch_chunks = chunks[i:i + batch]
            vectors = embed_texts([c["text"] for c in batch_chunks])
            for c, vec in zip(batch_chunks, vectors):
                rows.append(
                    models.Chunk(
                        document_id=doc.id,
                        page_number=c["page_number"],
                        chunk_index=c["chunk_index"],
                        text=c["text"],
                        embedding=vec,
                    )
                )
            # Flush in batches so 500-page PDFs don't blow memory.
            db.add_all(rows)
            db.commit()
            rows = []

        doc.total_pages = len(pages)
        doc.status = "ready"
        db.commit()
        return {
            "ok": True,
            "document_id": document_id,
            "total_pages": len(pages),
            "chunks": len(chunks),
        }
    except Exception as e:
        try:
            doc = (
                db.query(models.Document)
                .filter(models.Document.id == uuid.UUID(document_id))
                .first()
            )
            if doc:
                # Final failure only after retries exhausted; otherwise the
                # retry will re-run and set status back to processing.
                if self.request.retries >= 3:
                    doc.status = "failed"
                    doc.error = str(e)
                    db.commit()
        except Exception:
            pass
        raise
    finally:
        db.close()
