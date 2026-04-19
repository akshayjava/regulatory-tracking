"""
Regulations router — CRUD, filtering, stats.
"""
import json
from datetime import date, timedelta
from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..database import get_db, row_to_dict
from ..models import (
    DashboardStats,
    DeadlineAlert,
    RegulationCreate,
    RegulationListResponse,
    RegulationResponse,
    SourceStatus,
    VerticalInfo,
)

router = APIRouter(prefix="/regulations", tags=["regulations"])

VALID_VERTICALS = {"crypto", "fintech", "healthcare", "insurance", "saas"}
VALID_STATUSES = {"proposed", "final", "effective", "withdrawn", "superseded"}


def _build_regulation_response(row: dict, conn) -> RegulationResponse:
    reg_id = row["id"]
    cur = conn.execute(
        "SELECT vertical, relevance_score, is_critical FROM regulation_verticals WHERE regulation_id=?",
        (reg_id,),
    )
    verticals = [
        VerticalInfo(vertical=r[0], relevance_score=r[1], is_critical=bool(r[2]))
        for r in cur.fetchall()
    ]
    row["verticals"] = verticals
    return RegulationResponse(**row)


@router.get("/stats/summary", response_model=DashboardStats)
def get_stats():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM regulations").fetchone()[0]

        by_status = {}
        for row in conn.execute("SELECT status, COUNT(*) FROM regulations GROUP BY status"):
            by_status[row[0]] = row[1]

        by_vertical = {}
        for row in conn.execute("SELECT vertical, COUNT(*) FROM regulation_verticals GROUP BY vertical"):
            by_vertical[row[0]] = row[1]

        by_agency = {}
        for row in conn.execute(
            "SELECT a.abbreviation, COUNT(r.id) FROM regulations r JOIN agencies a ON r.agency_id=a.id GROUP BY a.id ORDER BY COUNT(r.id) DESC LIMIT 10"
        ):
            by_agency[row[0]] = row[1]

        today = date.today()
        d30 = conn.execute(
            "SELECT COUNT(*) FROM regulations WHERE deadline_date BETWEEN ? AND ?",
            (today.isoformat(), (today + timedelta(days=30)).isoformat()),
        ).fetchone()[0]
        d90 = conn.execute(
            "SELECT COUNT(*) FROM regulations WHERE deadline_date BETWEEN ? AND ?",
            (today.isoformat(), (today + timedelta(days=90)).isoformat()),
        ).fetchone()[0]

        sources = []
        for row in conn.execute("SELECT name, abbreviation, last_sync, status, regulation_count FROM regulatory_sources"):
            sources.append(SourceStatus(
                name=row[0], abbreviation=row[1],
                last_sync=row[2], status=row[3], regulation_count=row[4]
            ))

        return DashboardStats(
            total_regulations=total,
            by_status=by_status,
            by_vertical=by_vertical,
            by_agency=by_agency,
            deadlines_30_days=d30,
            deadlines_90_days=d90,
            sources=sources,
        )


@router.get("/alerts/deadlines", response_model=List[DeadlineAlert])
def get_deadline_alerts(days: int = Query(30, ge=1, le=365)):
    today = date.today()
    cutoff = (today + timedelta(days=days)).isoformat()
    with get_db() as conn:
        rows = conn.execute(
            """SELECT r.regulation_id, r.title, r.deadline_date, r.impact_score
               FROM regulations r
               WHERE r.deadline_date BETWEEN ? AND ?
               ORDER BY r.deadline_date ASC""",
            (today.isoformat(), cutoff),
        ).fetchall()

        alerts = []
        for row in rows:
            dl = date.fromisoformat(row[2])
            days_until = (dl - today).days
            urgency = "critical" if days_until <= 30 else "high" if days_until <= 60 else "medium"
            reg_row = conn.execute("SELECT id FROM regulations WHERE regulation_id=?", (row[0],)).fetchone()
            verticals = []
            if reg_row:
                v_rows = conn.execute(
                    "SELECT vertical FROM regulation_verticals WHERE regulation_id=?", (reg_row[0],)
                ).fetchall()
                verticals = [v[0] for v in v_rows]
            alerts.append(DeadlineAlert(
                regulation_id=row[0], title=row[1], deadline_date=dl,
                days_until=days_until, urgency=urgency, verticals=verticals,
                impact_score=row[3],
            ))
        return alerts


@router.get("/vertical/{vertical_name}", response_model=List[RegulationResponse])
def get_by_vertical(vertical_name: str, limit: int = Query(50, le=100)):
    if vertical_name not in VALID_VERTICALS:
        raise HTTPException(400, f"Invalid vertical. Valid: {sorted(VALID_VERTICALS)}")
    with get_db() as conn:
        rows = conn.execute(
            """SELECT r.* FROM regulations r
               JOIN regulation_verticals rv ON r.id = rv.regulation_id
               WHERE rv.vertical = ?
               ORDER BY r.impact_score DESC
               LIMIT ?""",
            (vertical_name, limit),
        ).fetchall()
        return [_build_regulation_response(row_to_dict(r), conn) for r in rows]


@router.get("/{regulation_id_slug}", response_model=RegulationResponse)
def get_regulation(regulation_id_slug: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM regulations WHERE regulation_id=?", (regulation_id_slug,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Regulation not found")
        return _build_regulation_response(row_to_dict(row), conn)


@router.get("/", response_model=RegulationListResponse)
def list_regulations(
    vertical: Optional[str] = None,
    status: Optional[str] = None,
    agency: Optional[str] = None,
    search: Optional[str] = None,
    deadline_within_days: Optional[int] = Query(None, ge=1, le=365),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    if vertical and vertical not in VALID_VERTICALS:
        raise HTTPException(400, f"Invalid vertical. Valid: {sorted(VALID_VERTICALS)}")
    if status and status not in VALID_STATUSES:
        raise HTTPException(400, f"Invalid status. Valid: {sorted(VALID_STATUSES)}")

    where_clauses = []
    params: List[Any] = []

    if vertical:
        where_clauses.append("r.id IN (SELECT regulation_id FROM regulation_verticals WHERE vertical=?)")
        params.append(vertical)
    if status:
        where_clauses.append("r.status=?")
        params.append(status)
    if agency:
        where_clauses.append("r.agency_id IN (SELECT id FROM agencies WHERE abbreviation=? OR name LIKE ?)")
        params.extend([agency, f"%{agency}%"])
    if search:
        where_clauses.append("(r.title LIKE ? OR r.summary LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
    if deadline_within_days:
        today = date.today()
        cutoff = (today + timedelta(days=deadline_within_days)).isoformat()
        where_clauses.append("r.deadline_date BETWEEN ? AND ?")
        params.extend([today.isoformat(), cutoff])

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    offset = (page - 1) * page_size

    with get_db() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM regulations r {where_sql}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT r.* FROM regulations r {where_sql} ORDER BY r.impact_score DESC LIMIT ? OFFSET ?",
            params + [page_size, offset],
        ).fetchall()
        items = [_build_regulation_response(row_to_dict(r), conn) for r in rows]
        return RegulationListResponse(
            items=items, total=total, page=page, page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )


@router.post("/", response_model=RegulationResponse, status_code=201)
def create_regulation(reg: RegulationCreate):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO regulations
               (regulation_id, title, type, status, source, summary,
                published_date, effective_date, deadline_date,
                complexity_score, impact_score, affected_entities, keywords, citation, agency_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                reg.regulation_id, reg.title, reg.type, reg.status, reg.source,
                reg.summary, str(reg.published_date) if reg.published_date else None,
                str(reg.effective_date) if reg.effective_date else None,
                str(reg.deadline_date) if reg.deadline_date else None,
                reg.complexity_score, reg.impact_score,
                json.dumps(reg.affected_entities), json.dumps(reg.keywords),
                reg.citation, reg.agency_id,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM regulations WHERE id=?", (cur.lastrowid,)).fetchone()
        return _build_regulation_response(row_to_dict(row), conn)


@router.put("/{regulation_id_slug}", response_model=RegulationResponse)
def update_regulation(regulation_id_slug: str, updates: dict):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM regulations WHERE regulation_id=?", (regulation_id_slug,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Regulation not found")

        allowed = {"title", "status", "deadline_date", "summary", "complexity_score", "impact_score"}
        set_clauses = []
        params = []
        for field, value in updates.items():
            if field in allowed:
                old_val = dict(row).get(field)
                if str(old_val) != str(value):
                    conn.execute(
                        "INSERT INTO regulation_history (regulation_id, field_changed, old_value, new_value) VALUES (?,?,?,?)",
                        (row["id"], field, str(old_val), str(value)),
                    )
                set_clauses.append(f"{field}=?")
                params.append(value)

        if set_clauses:
            conn.execute(
                f"UPDATE regulations SET {', '.join(set_clauses)} WHERE regulation_id=?",
                params + [regulation_id_slug],
            )
            conn.commit()

        updated = conn.execute(
            "SELECT * FROM regulations WHERE regulation_id=?", (regulation_id_slug,)
        ).fetchone()
        return _build_regulation_response(row_to_dict(updated), conn)
