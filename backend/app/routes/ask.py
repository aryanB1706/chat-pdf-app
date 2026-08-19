import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import cache, models, schemas
from ..agent import answer_question, plan_tools
from ..config import settings
from ..db import get_db
from ..gateway import estimate_tokens
from ..retrieval import retrieve_chunks

router = APIRouter()


def _answer_cache_key(document_id: uuid.UUID, question: str, top_k: int) -> str:
    normalized = " ".join(question.strip().lower().split())
    return f"ask:v1:{document_id}:{cache.sha_key(normalized, str(top_k))}"


def _log_query(
    db: Session,
    document_id: uuid.UUID,
    question: str,
    tools: list[str],
    model_used: str,
    fallback_used: bool,
    cached: bool,
    prompt: str,
    answer: str,
    latency_ms: float,
) -> None:
    try:
        db.add(
            models.QueryLog(
                document_id=document_id,
                question=question[:2000],
                tools_used=",".join(tools),
                model_used=model_used,
                fallback_used=fallback_used,
                cached=cached,
                prompt_tokens_est=estimate_tokens(prompt),
                completion_tokens_est=estimate_tokens(answer),
                latency_ms=latency_ms,
            )
        )
        db.commit()
    except Exception as e:
        print(f"[ask] logging failed: {e}")
        db.rollback()


@router.post("/ask", response_model=schemas.AskResponse)
def ask_question(body: schemas.AskRequest, db: Session = Depends(get_db)):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question is empty")
    top_k = max(1, min(body.top_k, 20))
    t0 = time.perf_counter()

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

    # Answer cache: repeat questions skip retrieval + LLM entirely.
    key = _answer_cache_key(doc.id, body.question, top_k)
    cached = cache.cache_get_json(key)
    if isinstance(cached, dict) and cached.get("answer"):
        ms = (time.perf_counter() - t0) * 1000
        _log_query(
            db, doc.id, body.question,
            cached.get("tools_used", ["retrieve"]),
            cached.get("model_used", "cache"),
            False, True,
            body.question, cached["answer"], ms,
        )
        return schemas.AskResponse(
            document_id=doc.id,
            question=body.question,
            answer=cached["answer"],
            citations=cached["citations"],
            tools_used=cached.get("tools_used", ["retrieve"]),
            cached=True,
            model_used=cached.get("model_used", "cache"),
        )

    tools = plan_tools(body.question)
    chunks = retrieve_chunks(db, doc.id, body.question, top_k=top_k)
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks indexed yet")

    result = answer_question(body.question, chunks, tools_used=tools)
    ms = (time.perf_counter() - t0) * 1000

    cache.cache_set_json(
        key,
        {
            "answer": result["answer"],
            "citations": result["citations"],
            "tools_used": result["tools_used"],
            "model_used": result["model_used"],
        },
        settings.answer_cache_ttl_s,
    )
    _log_query(
        db, doc.id, body.question, result["tools_used"],
        result["model_used"], result["fallback_used"], False,
        result.get("prompt", body.question), result["answer"], ms,
    )
    return schemas.AskResponse(
        document_id=doc.id,
        question=body.question,
        answer=result["answer"],
        citations=result["citations"],
        tools_used=result["tools_used"],
        cached=False,
        model_used=result["model_used"],
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
