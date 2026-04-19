"""
Deduplication utilities for the ingestion pipeline.
"""
import re
import sqlite3


def normalize_regulation_id(title: str, source: str, date: str) -> str:
    """Generate a consistent slug ID from title, source, and date."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s]", "", slug)
    slug = re.sub(r"\s+", "_", slug.strip())
    slug = slug[:60].rstrip("_")
    year = date[:4] if date else "0000"
    return f"{source}_{slug}_{year}"


def _title_similarity(a: str, b: str) -> float:
    """Simple word-overlap similarity between two titles."""
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    return len(intersection) / max(len(words_a), len(words_b))


def is_duplicate(reg: dict, conn: sqlite3.Connection) -> bool:
    """Check if regulation already exists in DB by ID or title similarity."""
    cur = conn.cursor()

    # Exact slug match
    cur.execute("SELECT id FROM regulations WHERE regulation_id = ?", (reg.get("regulation_id"),))
    if cur.fetchone():
        return True

    # Title similarity check (only if same source)
    cur.execute("SELECT title FROM regulations WHERE source = ? LIMIT 100", (reg.get("source", ""),))
    for row in cur.fetchall():
        if _title_similarity(reg.get("title", ""), row[0]) > 0.85:
            return True

    return False


def deduplicate(regulations: list[dict]) -> list[dict]:
    """Remove duplicates from a list of regulation dicts (in-memory)."""
    seen_ids: set[str] = set()
    seen_titles: list[str] = []
    unique: list[dict] = []

    for reg in regulations:
        reg_id = reg.get("regulation_id", "")
        title = reg.get("title", "")

        if reg_id in seen_ids:
            continue

        is_dup = any(_title_similarity(title, t) > 0.85 for t in seen_titles)
        if is_dup:
            continue

        seen_ids.add(reg_id)
        seen_titles.append(title)
        unique.append(reg)

    return unique
