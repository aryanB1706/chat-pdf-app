import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    file_size_bytes: int
    total_pages: int
    status: str
    error: str | None = None
    created_at: datetime
    chunk_count: int = 0

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    document_id: uuid.UUID
    filename: str
    status: str
    message: str


class AskRequest(BaseModel):
    document_id: uuid.UUID
    question: str
    top_k: int = 5


class Citation(BaseModel):
    page: int
    chunk_index: int
    excerpt: str


class AskResponse(BaseModel):
    document_id: uuid.UUID
    question: str
    answer: str
    citations: list[Citation]
    tools_used: list[str]
    cached: bool = False
    model_used: str = ""


class QueryLogOut(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID | None
    question: str
    tools_used: str
    model_used: str
    fallback_used: bool
    cached: bool
    prompt_tokens_est: int
    completion_tokens_est: int
    latency_ms: float
    created_at: datetime

    class Config:
        from_attributes = True


class StatsOut(BaseModel):
    total_queries: int
    cache_hits: int
    cache_hit_rate: float
    fallback_count: int
    avg_latency_ms: float
    est_tokens_total: int
    est_tokens_saved_by_cache: int
