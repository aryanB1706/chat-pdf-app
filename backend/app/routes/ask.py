import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..agent import answer_question, plan_tools
from ..db import get_db
from ..retrieval import retrieve_chunks

router = APIRouter()


@router.post("/ask", response_model=schemas.AskResponse)
def ask_question(body: schemas.AskRequest, db: Session = Depends(get_db)):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question is empty")
    top_k = max(1, min(body.top_k, 20))

    doc = (
        db.query(models.Document)
        .filter(models.Document.id == body.document_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.status != "ready":
        raise HTTPException(
            status_code=409,
            detail=f"Document not ready (status={doc.status}). "
            "Check GET /documents/{id}/status.",
        )

    tools = plan_tools(body.question)
    chunks = retrieve_chunks(db, doc.id, body.question, top_k=top_k)
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks indexed yet")

    result = answer_question(body.question, chunks, tools_used=tools)
    return schemas.AskResponse(
        document_id=doc.id,
        question=body.question,
        answer=result["answer"],
        citations=result["citations"],
        tools_used=result["tools_used"],
    )


@router.get("/documents/{document_id}/citations/check")
def citation_check(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """Debug helper: confirm every chunk carries a page number."""
    chunks = (
        db.query(models.Chunk)
        .filter(models.Chunk.document_id == document_id)
        .limit(100)
        .all()
    )
    missing = [str(c.id) for c in chunks if not c.page_number]
    return {
        "document_id": str(document_id),
        "checked": len(chunks),
        "missing_page": len(missing),
        "ok": len(missing) == 0,
    }
