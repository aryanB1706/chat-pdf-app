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
