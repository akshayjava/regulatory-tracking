"""
Sources router — regulatory source health, ingestion status, and manual sync.
"""
from __future__ import annotations
import sys
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from ..database import get_db, row_to_dict
from ..models import SourceStatus

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/", response_model=list[SourceStatus])
def list_sources():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT name, abbreviation, last_sync, status, regulation_count FROM regulatory_sources ORDER BY name"
        ).fetchall()
        return [SourceStatus(**dict(r)) for r in rows]


@router.get("/health")
def sources_health():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT name, abbreviation, last_sync, status, regulation_count FROM regulatory_sources"
        ).fetchall()
        health = []
        for r in rows:
            health.append({
                "name": r["name"],
                "abbreviation": r["abbreviation"],
                "status": r["status"],
                "last_sync": r["last_sync"],
                "regulation_count": r["regulation_count"],
                "healthy": r["status"] == "active",
            })
        overall = "ok" if all(h["healthy"] for h in health) else "degraded"
        return {"status": overall, "sources": health}


@router.get("/ingestion-status")
def ingestion_status():
    """
    Return per-source ingestion status: last sync, regulation count,
    recent errors, and next scheduled sync from APScheduler.
    """
    from api.main import _scheduler  # type: ignore

    next_run = None
    if _scheduler is not None:
        job = _scheduler.get_job("daily_ingestion")
        if job and job.next_run_time:
            next_run = job.next_run_time.isoformat()

    with get_db() as conn:
        sources = conn.execute(
            "SELECT name, abbreviation, last_sync, status, regulation_count FROM regulatory_sources ORDER BY name"
        ).fetchall()

        # Pull recent error-like update records (last 20 entries with urgency=critical)
        recent_updates = conn.execute(
            """SELECT r.regulation_id, r.title, ru.update_type, ru.urgency, ru.detected_at
               FROM regulation_updates ru
               JOIN regulations r ON r.id = ru.regulation_id
               ORDER BY ru.detected_at DESC LIMIT 20"""
        ).fetchall()

        total = conn.execute("SELECT COUNT(*) FROM regulations").fetchone()[0]

        # Per-vertical counts
        vertical_counts = {}
        for row in conn.execute("SELECT vertical, COUNT(*) FROM regulation_verticals GROUP BY vertical"):
            vertical_counts[row[0]] = row[1]

    source_list = []
    for s in sources:
        source_list.append({
            "name": s["name"],
            "abbreviation": s["abbreviation"],
            "last_sync": s["last_sync"],
            "status": s["status"],
            "regulation_count": s["regulation_count"],
            "healthy": s["status"] == "active",
        })

    updates = [
        {
            "regulation_id": u["regulation_id"],
            "title": u["title"],
            "update_type": u["update_type"],
            "urgency": u["urgency"],
            "detected_at": u["detected_at"],
        }
        for u in recent_updates
    ]

    return {
        "total_regulations": total,
        "vertical_breakdown": vertical_counts,
        "next_scheduled_sync": next_run,
        "scheduler_active": _scheduler is not None and _scheduler.running,
        "sources": source_list,
        "recent_updates": updates,
    }


@router.post("/sync/{source_name}")
def trigger_sync(source_name: str):
    """Trigger manual ingestion sync for a specific source."""
    valid = {"congress", "federal_register", "healthcare", "legiscan"}
    if source_name not in valid:
        raise HTTPException(400, f"Invalid source. Valid: {sorted(valid)}")

    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from ingestion.pipeline import IngestionPipeline
        pipeline = IngestionPipeline()
        stats = pipeline.run(source_name=source_name)
        return {"status": "ok", "source": source_name, "stats": stats}
    except Exception as e:
        raise HTTPException(500, f"Sync failed: {str(e)}")
