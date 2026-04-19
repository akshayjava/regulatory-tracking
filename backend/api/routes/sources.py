"""
Sources router — regulatory source health and manual sync.
"""
from __future__ import annotations
import sys
import os
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
