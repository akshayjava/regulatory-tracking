"""
Alerts router — deadlines, new regulations, critical updates.
"""
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Query

from ..database import get_db

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/deadlines")
def get_deadlines(days: int = Query(30, ge=1, le=365)):
    today = date.today()
    cutoff = (today + timedelta(days=days)).isoformat()
    with get_db() as conn:
        # ⚡ Bolt Optimization: Use GROUP_CONCAT to fetch verticals in the same query (N+1 -> 1)
        rows = conn.execute(
            """SELECT r.regulation_id, r.title, r.deadline_date, r.impact_score, r.status,
                      GROUP_CONCAT(rv.vertical) as verticals_str
               FROM regulations r
               LEFT JOIN regulation_verticals rv ON r.id = rv.regulation_id
               WHERE r.deadline_date BETWEEN ? AND ?
               GROUP BY r.id
               ORDER BY r.deadline_date ASC""",
            (today.isoformat(), cutoff),
        ).fetchall()

        results = []
        for row in rows:
            dl = date.fromisoformat(row["deadline_date"])
            days_until = (dl - today).days
            urgency = "critical" if days_until <= 14 else "high" if days_until <= 30 else "medium"

            verticals = []
            if row["verticals_str"]:
                verticals = row["verticals_str"].split(",")

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
