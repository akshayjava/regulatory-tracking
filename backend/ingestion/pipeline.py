"""
LATTICE Ingestion Pipeline
Orchestrates all regulatory sources, deduplicates, and persists to SQLite.
"""
from __future__ import annotations
import json
import logging
import os
import sqlite3
from datetime import date, datetime
from typing import Any

from .deduplication import deduplicate, is_duplicate, normalize_regulation_id
from .sources import CongressSource, FederalRegisterSource, HealthcareSource, LegiScanSource

logger = logging.getLogger(__name__)

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "schema.sql")


def _detect_urgency(reg: dict) -> str:
    deadline = reg.get("deadline_date")
    impact = reg.get("impact_score", 5)
    if deadline:
        days = (date.fromisoformat(deadline) - date.today()).days
        if days <= 30:
            return "critical"
        if days <= 90:
            return "high"
    if impact >= 9:
        return "high"
    if impact >= 7:
        return "medium"
    return "low"


class IngestionPipeline:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or os.environ.get("DB_PATH", "lattice.db")
        self.sources = {
            "congress": CongressSource(),
            "federal_register": FederalRegisterSource(),
            "healthcare": HealthcareSource(),
            "legiscan": LegiScanSource(),
        }
        self._stats = {"new": 0, "updated": 0, "skipped": 0, "errors": 0}

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self, conn: sqlite3.Connection):
        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH) as f:
                conn.executescript(f.read())
            conn.commit()

    def _get_or_create_agency(self, conn: sqlite3.Connection, name: str) -> int | None:
        if not name:
            return None
        cur = conn.cursor()
        cur.execute("SELECT id FROM agencies WHERE abbreviation = ? OR name = ?", (name, name))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO agencies (name, abbreviation) VALUES (?,?)", (name, name))
        conn.commit()
        return cur.lastrowid

    def _save_regulation(self, conn: sqlite3.Connection, reg: dict) -> str:
        """Upsert a regulation. Returns 'new', 'updated', or 'skipped'."""
        cur = conn.cursor()

        # Ensure regulation_id
        if not reg.get("regulation_id"):
            reg["regulation_id"] = normalize_regulation_id(
                reg.get("title", ""), reg.get("source", "unknown"), reg.get("published_date", "")
            )

        if is_duplicate(reg, conn):
            return "skipped"

        agency_id = self._get_or_create_agency(conn, reg.get("agency", ""))

        cur.execute(
            """INSERT INTO regulations
               (regulation_id, title, type, status, source, summary,
                published_date, effective_date, deadline_date,
                complexity_score, impact_score,
                affected_entities, keywords, citation, agency_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(regulation_id) DO UPDATE SET
                 status=excluded.status,
                 deadline_date=excluded.deadline_date,
                 updated_at=CURRENT_TIMESTAMP""",
            (
                reg["regulation_id"],
                reg.get("title", "")[:500],
                reg.get("type", "notice"),
                reg.get("status", "proposed"),
                reg.get("source", "unknown"),
                reg.get("summary", "")[:2000],
                reg.get("published_date"),
                reg.get("effective_date"),
                reg.get("deadline_date"),
                reg.get("complexity_score", 5),
                reg.get("impact_score", 5),
                json.dumps(reg.get("affected_entities", [])),
                json.dumps(reg.get("keywords", [])),
                reg.get("citation"),
                agency_id,
            ),
        )

        is_new = cur.rowcount == 1 or conn.execute(
            "SELECT changes()"
        ).fetchone()[0] > 0

        reg_db_id = cur.execute(
            "SELECT id FROM regulations WHERE regulation_id=?", (reg["regulation_id"],)
        ).fetchone()[0]

        # Verticals
        for vertical, score, critical in reg.get("verticals", []):
            cur.execute(
                """INSERT OR IGNORE INTO regulation_verticals
                   (regulation_id, vertical, relevance_score, is_critical)
                   VALUES (?,?,?,?)""",
                (reg_db_id, vertical, score, 1 if critical else 0),
            )

        # Update record
        urgency = _detect_urgency(reg)
        cur.execute(
            """INSERT INTO regulation_updates (regulation_id, update_type, urgency)
               VALUES (?,?,?)""",
            (reg_db_id, "new_regulation", urgency),
        )

        conn.commit()
        return "new"

    def run(self, source_name: str | None = None) -> dict[str, Any]:
        """Run ingestion for all sources (or a specific one). Returns stats dict."""
        self._stats = {"new": 0, "updated": 0, "skipped": 0, "errors": 0}
        conn = self._get_conn()
        self._init_db(conn)

        sources_to_run = (
            {source_name: self.sources[source_name]}
            if source_name and source_name in self.sources
            else self.sources
        )

        all_regs: list[dict] = []
        for name, source in sources_to_run.items():
            try:
                logger.info(f"Running source: {name}")
                if name in ("healthcare", "legiscan"):
                    regs = source.fetch()
                else:
                    regs = source.fetch(limit=50)
                logger.info(f"  {name}: fetched {len(regs)} regulations")
                all_regs.extend(regs)
            except Exception as e:
                logger.error(f"  {name} failed: {e}")
                self._stats["errors"] += 1

        unique_regs = deduplicate(all_regs)
        logger.info(f"After dedup: {len(unique_regs)} unique regulations (from {len(all_regs)})")

        for reg in unique_regs:
            try:
                result = self._save_regulation(conn, reg)
                self._stats[result] = self._stats.get(result, 0) + 1
            except Exception as e:
                logger.error(f"Error saving {reg.get('regulation_id')}: {e}")
                self._stats["errors"] += 1

        conn.close()
        logger.info(f"Ingestion complete: {self._stats}")
        return {**self._stats, "total_processed": len(unique_regs)}
