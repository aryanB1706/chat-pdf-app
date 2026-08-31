"""Studio endpoints: quiz, mindmap, podcast, crop analysis.

Ported from the legacy Node backend with identical response shapes so the
React tabs keep working. LLM path uses the model gateway (with fallback);
any LLM/parse failure degrades to deterministic builders so the endpoints
always return valid shapes — except vision, which genuinely needs a key.
"""

import base64
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import settings
from ..db import get_db
from ..gateway import generate_json, generate_vision

router = APIRouter()

_SAMPLE_LIMIT = 40
_CONTEXT_CHARS = 12000


def _require_ready_doc(db: Session, document_id: uuid.UUID) -> models.Document:
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.status != "ready":
        raise HTTPException(
            status_code=409,
            detail=f"Document not ready (status={doc.status}).",
        )
    return doc


def _sample_chunks(db: Session, doc_id: uuid.UUID) -> list[dict]:
    """Evenly spaced chunks across the whole document (long-doc safe)."""
    total = (
        db.query(func.count(models.Chunk.id))
        .filter(models.Chunk.document_id == doc_id)
        .scalar()
        or 0
    )
    if total == 0:
        raise HTTPException(status_code=404, detail="No chunks indexed yet")
    ids = [
        r[0]
        for r in db.query(models.Chunk.id)
        .filter(models.Chunk.document_id == doc_id)
        .order_by(models.Chunk.chunk_index)
        .all()
    ]
    stride = max(1, len(ids) // _SAMPLE_LIMIT)
    picked = ids[::stride][:_SAMPLE_LIMIT]
    rows = (
        db.query(models.Chunk)
        .filter(models.Chunk.id.in_(picked))
        .order_by(models.Chunk.chunk_index)
        .all()
    )
    return [
        {"page_number": c.page_number, "chunk_index": c.chunk_index, "text": c.text}
        for c in rows
    ]


def _context(samples: list[dict]) -> str:
    text = "\n\n".join(f"[Page {s['page_number']}] {s['text']}" for s in samples)
    return text[:_CONTEXT_CHARS]


# --- Deterministic fallbacks (no key / LLM failure) ---

def _fallback_quiz(samples: list[dict], n: int) -> list[dict]:
    items, m = [], len(samples)
    for i in range(min(n, m)):
        correct = samples[i]["text"][:160].strip()
        page = samples[i]["page_number"]
        distractors = [samples[(i + j) % m]["text"][:160].strip() for j in (1, 2, 3)]
        pos = i % 4
        options = distractors[:]
        options.insert(pos, correct)
        items.append(
            {
                "question": f"According to page {page}, which statement is correct?",
                "options": options,
                "answer": pos,
                "explanation": f"Stated on page {page}: {correct[:200]}",
            }
        )
    return items


def _fallback_mindmap(samples: list[dict], title: str) -> dict:
    seen: dict[int, str] = {}
    for s in samples:
        seen.setdefault(s["page_number"], s["text"][:60].strip())
    pages = sorted(seen)[:12]
    nodes = [{"id": "root", "position": {"x": 250, "y": 0}, "data": {"label": title}}]
    edges = []
    for i, p in enumerate(pages):
        nodes.append(
            {
                "id": f"p{p}",
                "position": {"x": i * 180, "y": 150},
                "data": {"label": f"Page {p}: {seen[p]}"},
            }
        )
        edges.append({"id": f"e-root-p{p}", "source": "root", "target": f"p{p}"})
    return {"nodes": nodes, "edges": edges}


def _fallback_podcast(samples: list[dict], hinglish: bool) -> str:
    flavor = "Arre wah! " if hinglish else ""
    lines = []
    for i, s in enumerate(s for s in samples[:6]):
        host = "Host A" if i % 2 == 0 else "Host B"
        lines.append(f"{host}: {flavor}On page {s['page_number']}: {s['text'][:220].strip()}")
    return "2-minute study podcast script:\n\n" + "\n\n".join(lines)


# --- Endpoints ---

@router.post("/quiz", response_model=list[schemas.QuizItem])
def generate_quiz(body: schemas.QuizRequest, db: Session = Depends(get_db)):
    n = max(1, min(body.num_questions, 10))
    _require_ready_doc(db, body.document_id)
    samples = _sample_chunks(db, body.document_id)
    if settings.gemini_api_key:
        try:
            data, _, _, _ = generate_json(
                "Based on the text below, generate "
                f"{n} multiple choice questions. Return ONLY a JSON array. "
                'Format: [{"question": "...", "options": ["...", "...", "...", "..."], '
                '"answer": 0, "explanation": "..."}]\n\n'
                f"Text:\n{_context(samples)}"
            )
            items = [
                schemas.QuizItem(
                    question=str(q["question"]),
                    options=[str(o) for o in q["options"][:4]],
                    answer=int(q["answer"]) % 4,
                    explanation=str(q.get("explanation", "")),
                )
                for q in data[:n]
            ]
            if items:
                return items
        except Exception as e:
            print(f"[studio] quiz LLM failed, fallback: {e}")
    return _fallback_quiz(samples, n)


@router.post("/mindmap", response_model=schemas.MindMapResponse)
def generate_mindmap(body: schemas.MindMapRequest, db: Session = Depends(get_db)):
    doc = _require_ready_doc(db, body.document_id)
    samples = _sample_chunks(db, body.document_id)
    if settings.gemini_api_key:
        try:
            data, _, _, _ = generate_json(
                "Create a hierarchical concept map. Return ONLY JSON with "
                "'nodes' and 'edges' for ReactFlow. "
                "Root at {x: 250, y: 0}. "
                f"Text:\n{_context(samples)}"
            )
            if isinstance(data, dict) and data.get("nodes"):
                return {"nodes": data["nodes"], "edges": data.get("edges", [])}
        except Exception as e:
            print(f"[studio] mindmap LLM failed, fallback: {e}")
    return _fallback_mindmap(samples, doc.filename)


@router.post("/podcast", response_model=schemas.PodcastResponse)
def generate_podcast(body: schemas.PodcastRequest, db: Session = Depends(get_db)):
    _require_ready_doc(db, body.document_id)
    samples = _sample_chunks(db, body.document_id)
    hinglish = body.language == "hinglish"
    lang_instruction = (
        "Use Hinglish (Hindi+English). Fun & casual tone."
        if hinglish
        else "Use clear, engaging English."
    )
    if settings.gemini_api_key:
        try:
            from ..gateway import generate as gateway_generate

            text, _, _, _ = gateway_generate(
                "Convert the text below to a 2-minute podcast script "
                f"between Host A and Host B. {lang_instruction}\n\n"
                f"Text:\n{_context(samples)}"
            )
            return {"script": text}
        except Exception as e:
            print(f"[studio] podcast LLM failed, fallback: {e}")
    return {"script": _fallback_podcast(samples, hinglish)}


@router.post("/analyze-crop", response_model=schemas.CropResponse)
def analyze_crop(body: schemas.CropRequest):
    raw = body.image.split(",", 1)[1] if "," in body.image else body.image
    try:
        image_bytes = base64.b64decode(raw)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image data")
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="Vision analysis needs GEMINI_API_KEY configured.",
        )
    try:
        text, _, _, _ = generate_vision(
            body.question or "Explain this image.", image_bytes
        )
        return {"reply": text}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Vision model failed: {e}")
