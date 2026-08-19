from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import init_db
from .routes import ask, documents, health, jobs, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create extension + tables if DB is reachable; otherwise serve degraded
    # (/health will report postgres status).
    try:
        init_db()
    except Exception as e:
        print(f"[startup] DB init skipped: {e}")
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router, tags=["health"])
    app.include_router(
        documents.router, prefix=settings.api_v1_prefix, tags=["documents"]
    )
    app.include_router(jobs.router, prefix=settings.api_v1_prefix, tags=["jobs"])
    app.include_router(ask.router, prefix=settings.api_v1_prefix, tags=["agent"])
    app.include_router(stats.router, prefix=settings.api_v1_prefix, tags=["stats"])
    return app


app = create_app()


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "health": "/health",
        "upload": f"{settings.api_v1_prefix}/documents/upload",
        "ask": f"{settings.api_v1_prefix}/ask",
    }
