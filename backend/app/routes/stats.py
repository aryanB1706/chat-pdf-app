from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db

router = APIRouter()


@router.get("/stats", response_model=schemas.StatsOut)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(models.QueryLog.id)).scalar() or 0
    hits = (
        db.query(func.count(models.QueryLog.id))
        .filter(models.QueryLog.cached.is_(True))
        .scalar()
        or 0
    )
    fallbacks = (
        db.query(func.count(models.QueryLog.id))
        .filter(models.QueryLog.fallback_used.is_(True))
        .scalar()
        or 0
    )
    avg_lat = db.query(func.avg(models.QueryLog.latency_ms)).scalar() or 0.0
    tokens_total = (
        db.query(
            func.coalesce(func.sum(models.QueryLog.prompt_tokens_est), 0)
            + func.coalesce(func.sum(models.QueryLog.completion_tokens_est), 0)
        ).scalar()
        or 0
    )
    tokens_saved = (
        db.query(
            func.coalesce(func.sum(models.QueryLog.prompt_tokens_est), 0)
            + func.coalesce(func.sum(models.QueryLog.completion_tokens_est), 0)
        )
        .filter(models.QueryLog.cached.is_(True))
        .scalar()
        or 0
    )
    return schemas.StatsOut(
        total_queries=total,
        cache_hits=hits,
        cache_hit_rate=round(hits / total, 3) if total else 0.0,
        fallback_count=fallbacks,
        avg_latency_ms=round(float(avg_lat), 2),
        est_tokens_total=int(tokens_total),
        est_tokens_saved_by_cache=int(tokens_saved),
    )


@router.get("/logs", response_model=list[schemas.QueryLogOut])
def recent_logs(limit: int = 20, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 100))
    return (
        db.query(models.QueryLog)
        .order_by(models.QueryLog.created_at.desc())
        .limit(limit)
        .all()
    )
