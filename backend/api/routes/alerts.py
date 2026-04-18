"""
Alerts router — deadlines, new regulations, critical updates.
"""
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Query

from ..database import get_db, row_to_dict

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/deadlines")
def get_deadlines(days: int = Query(30, ge=1, le=365)):
    today = date.today()
    cutoff = (today + timedelta(days=days)).isoformat()
    with get_db() as conn:
        rows = conn.execute(
            """SELECT r.regulation_id, r.title, r.deadline_date, r.impact_score, r.status
               FROM regulations r
               WHERE r.deadline_date BETWEEN ? AND ?
               ORDER BY r.deadline_date ASC""",
            (today.isoformat(), cutoff),
        ).fetchall()

        results = []
        for row in rows:
            dl = date.fromisoformat(row["deadline_date"])
            days_until = (dl - today).days
            urgency = "critical" if days_until <= 14 else "high" if days_until <= 30 else "medium"

            reg_id_row = conn.execute(
                "SELECT id FROM regulations WHERE regulation_id=?", (row["regulation_id"],)
            ).fetchone()
            verticals = []
            if reg_id_row:
                v_rows = conn.execute(
                    "SELECT vertical FROM regulation_verticals WHERE regulation_id=?", (reg_id_row[0],)
                ).fetchall()
                verticals = [v[0] for v in v_rows]

            results.append({
                "regulation_id": row["regulation_id"],
                "title": row["title"],
                "deadline_date": row["deadline_date"],
                "days_until": days_until,
                "urgency": urgency,
                "verticals": verticals,
                "impact_score": row["impact_score"],
                "status": row["status"],
            })
        return results


@router.get("/new")
def get_new_regulations(hours: int = Query(24, ge=1, le=168)):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    with get_db() as conn:
        rows = conn.execute(
            """SELECT r.regulation_id, r.title, r.source, r.status, r.impact_score, r.created_at
               FROM regulations r
               WHERE r.created_at >= ?
               ORDER BY r.created_at DESC""",
            (cutoff.isoformat(),),
        ).fetchall()
        return [dict(r) for r in rows]


@router.get("/critical")
def get_critical_alerts():
    with get_db() as conn:
        rows = conn.execute(
            """SELECT ru.id, ru.update_type, ru.detected_at, ru.urgency, ru.details,
                      r.regulation_id, r.title, r.deadline_date
               FROM regulation_updates ru
               JOIN regulations r ON ru.regulation_id = r.id
               WHERE ru.urgency IN ('critical', 'high')
               ORDER BY ru.detected_at DESC
               LIMIT 50""",
        ).fetchall()
        return [dict(r) for r in rows]
