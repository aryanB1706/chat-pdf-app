from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "chat-pdf-agentic-api"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql://postgres:postgres@localhost:5432/chatpdf"
    redis_url: str = "redis://localhost:6379/0"

    upload_dir: str = "/tmp/chatpdf_uploads"
    max_upload_mb: int = 100

    # Celery (Phase 2)
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Ingestion chunking (Phase 2) — tuned for 500-page PDFs
    chunk_size_chars: int = 1000
    chunk_overlap_chars: int = 200
    embedding_batch_size: int = 32

    # Model gateway (Phase 4)
    gemini_api_key: str = ""
    primary_llm_model: str = "gemini-flash-latest"
    secondary_llm_model: str = "gemini-1.5-flash-latest"
    llm_timeout_s: int = 30
    # Redis caching (Phase 4) — drives the "40% lower token cost" claim
    answer_cache_ttl_s: int = 3600
    embedding_cache_ttl_s: int = 604800  # 7 days

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
