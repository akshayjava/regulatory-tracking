"""
Database connection and helpers for LATTICE API.
"""
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = os.environ.get("DB_PATH", "lattice.db")
SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert sqlite3.Row to dict, parsing JSON fields."""
    d = dict(row)
    for key in ("affected_entities", "keywords", "compliance_requirements", "details"):
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                pass
    return d


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize database schema if not already created."""
    if SCHEMA_PATH.exists():
        with sqlite3.connect(DB_PATH) as conn:
            conn.executescript(SCHEMA_PATH.read_text())
            conn.commit()


def get_regulation_count() -> int:
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) FROM regulations").fetchone()
        return row[0] if row else 0
