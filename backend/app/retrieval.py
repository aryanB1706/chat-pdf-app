"""Vector retrieval over pgvector chunks."""

from sqlalchemy.orm import Session

from . import models
from .embeddings import embed_query


def retrieve_chunks(
    db: Session,
    document_id,
    question: str,
    top_k: int = 5,
) -> list[dict]:
    """Top-k chunks by cosine distance. Returns dicts with page + text + score."""
    query_vec = embed_query(question)
    rows = (
        db.query(models.Chunk, models.Chunk.embedding.cosine_distance(query_vec).label("dist"))
        .filter(models.Chunk.document_id == document_id)
        .order_by("dist")
        .limit(top_k)
        .all()
    )
    out: list[dict] = []
    for chunk, dist in rows:
        out.append(
            {
                "chunk_id": str(chunk.id),
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "score": float(dist) if dist is not None else 0.0,
            }
        )
    return out
