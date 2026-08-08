from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "chat-pdf-agentic-api"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql://postgres:postgres@localhost:5432/chatpdf"
    redis_url: str = "redis://localhost:6379/0"

    upload_dir: str = "/tmp/chatpdf_uploads"
    max_upload_mb: int = 100

    # Filled in later phases (gateway / embeddings)
    gemini_api_key: str = ""
    primary_llm_model: str = "gemini-flash-latest"
    secondary_llm_model: str = "gemini-flash-latest"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
