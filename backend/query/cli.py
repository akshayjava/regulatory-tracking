"""
LATTICE CLI — query and manage the regulatory database.

Usage:
  python -m query.cli stats
  python -m query.cli search --vertical crypto --status effective
  python -m query.cli ingest --source congress
  python -m query.cli export --vertical fintech --output fintech.csv
  python -m query.cli deadlines --days 30
"""
import csv
import json
import os
import sqlite3
import sys
from datetime import date, timedelta

import click

DB_PATH = os.environ.get("DB_PATH", "lattice.db")


def get_conn():
    if not os.path.exists(DB_PATH):
        click.echo(f"Database not found: {DB_PATH}", err=True)
        click.echo("Run: python db/seed_data.py", err=True)
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _row(label, value, width=28):
    click.echo(f"  {label:<{width}} {value}")


def _divider(char="─", width=60):
    click.echo(char * width)


@click.group()
def cli():
    """LATTICE — Regulatory Compliance Database CLI"""


@cli.command()
def stats():
    """Show database statistics."""
    conn = get_conn()
    _divider("═")
    click.echo("  LATTICE Database Statistics")
    _divider("═")

    total = conn.execute("SELECT COUNT(*) FROM regulations").fetchone()[0]
    _row("Total regulations:", total)

    click.echo()
    click.echo("  By Status:")
    for row in conn.execute("SELECT status, COUNT(*) as c FROM regulations GROUP BY status ORDER BY c DESC"):
        _row(f"    {row[0]}", row[1])

    click.echo()
    click.echo("  By Vertical:")
    for row in conn.execute("SELECT vertical, COUNT(*) as c FROM regulation_verticals GROUP BY vertical ORDER BY c DESC"):
        _row(f"    {row[0]}", row[1])

    click.echo()
    click.echo("  By Agency:")
    for row in conn.execute(
        "SELECT a.abbreviation, COUNT(r.id) as c FROM regulations r JOIN agencies a ON r.agency_id=a.id GROUP BY a.id ORDER BY c DESC LIMIT 10"
    ):
        _row(f"    {row[0]}", row[1])

    click.echo()
    today = date.today()
    d30 = conn.execute(
        "SELECT COUNT(*) FROM regulations WHERE deadline_date BETWEEN ? AND ?",
        (today.isoformat(), (today + timedelta(days=30)).isoformat()),
    ).fetchone()[0]
    _row("Deadlines in 30 days:", d30)
    _divider()
    conn.close()


@cli.command()
@click.option("--vertical", "-v", default=None, help="Filter by vertical (crypto, fintech, healthcare, insurance, saas)")
@click.option("--status", "-s", default=None, help="Filter by status (proposed, final, effective)")
@click.option("--agency", "-a", default=None, help="Filter by agency abbreviation (e.g. SEC, FDA)")
@click.option("--days", "-d", default=None, type=int, help="Only show regulations with deadlines within N days")
@click.option("--query", "-q", default=None, help="Text search in title and summary")
@click.option("--limit", "-l", default=20, show_default=True, help="Max results to show")
def search(vertical, status, agency, days, query, limit):
    """Search and filter regulations."""
    conn = get_conn()
    sql = "SELECT r.*, a.abbreviation as agency_name FROM regulations r LEFT JOIN agencies a ON r.agency_id=a.id"
    where, params = [], []

    if vertical:
        where.append("r.id IN (SELECT regulation_id FROM regulation_verticals WHERE vertical=?)")
        params.append(vertical)
    if status:
        where.append("r.status=?")
        params.append(status)
    if agency:
        where.append("(a.abbreviation=? OR a.name LIKE ?)")
        params.extend([agency, f"%{agency}%"])
    if days:
        today = date.today()
        where.append("r.deadline_date BETWEEN ? AND ?")
        params.extend([today.isoformat(), (today + timedelta(days=days)).isoformat()])
    if query:
        where.append("(r.title LIKE ? OR r.summary LIKE ?)")
        params.extend([f"%{query}%", f"%{query}%"])

    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY r.impact_score DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    click.echo(f"\n  Found {len(rows)} regulations\n")
    _divider()

    for r in rows:
        click.echo(f"  [{r['status'].upper():10}] {r['title'][:70]}")
        click.echo(f"             Agency: {r['agency_name'] or 'N/A'}  |  Impact: {r['impact_score'] or '?'}/10  |  Source: {r['source']}")
        if r['deadline_date']:
            days_left = (date.fromisoformat(r['deadline_date']) - date.today()).days
            click.echo(f"             Deadline: {r['deadline_date']} ({days_left} days)")
        click.echo()

    conn.close()


@cli.command()
@click.option("--source", "-s", default=None, help="Specific source to sync (congress, federal_register, healthcare, legiscan). Omit for all.")
def ingest(source):
    """Run the ingestion pipeline."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    try:
        from ingestion.pipeline import IngestionPipeline
    except ImportError as e:
        click.echo(f"Import error: {e}", err=True)
        sys.exit(1)

    click.echo(f"Running ingestion{'for ' + source if source else ' for all sources'}...")
    pipeline = IngestionPipeline()
    stats = pipeline.run(source_name=source)
    click.echo(f"  New:     {stats.get('new', 0)}")
    click.echo(f"  Updated: {stats.get('updated', 0)}")
    click.echo(f"  Skipped: {stats.get('skipped', 0)}")
    click.echo(f"  Errors:  {stats.get('errors', 0)}")


@cli.command()
@click.option("--vertical", "-v", default=None, help="Filter by vertical")
@click.option("--status", "-s", default=None, help="Filter by status")
@click.option("--output", "-o", default="export.csv", show_default=True, help="Output CSV filename")
def export(vertical, status, output):
    """Export regulations to CSV."""
    conn = get_conn()
    sql = "SELECT r.regulation_id, r.title, r.type, r.status, r.source, r.published_date, r.effective_date, r.deadline_date, r.complexity_score, r.impact_score, r.citation, a.abbreviation as agency FROM regulations r LEFT JOIN agencies a ON r.agency_id=a.id"
    where, params = [], []

    if vertical:
        where.append("r.id IN (SELECT regulation_id FROM regulation_verticals WHERE vertical=?)")
        params.append(vertical)
    if status:
        where.append("r.status=?")
        params.append(status)

    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY r.impact_score DESC"

    rows = conn.execute(sql, params).fetchall()
    fields = ["regulation_id", "title", "type", "status", "source", "published_date",
              "effective_date", "deadline_date", "complexity_score", "impact_score", "citation", "agency"]

    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))

    click.echo(f"Exported {len(rows)} regulations to {output}")
    conn.close()


@cli.command()
@click.option("--days", "-d", default=30, show_default=True, help="Show deadlines within N days")
def deadlines(days):
    """Show upcoming compliance deadlines."""
    conn = get_conn()
    today = date.today()
    cutoff = (today + timedelta(days=days)).isoformat()

    rows = conn.execute(
        """SELECT r.regulation_id, r.title, r.deadline_date, r.impact_score, a.abbreviation as agency
           FROM regulations r
           LEFT JOIN agencies a ON r.agency_id=a.id
           WHERE r.deadline_date BETWEEN ? AND ?
           ORDER BY r.deadline_date ASC""",
        (today.isoformat(), cutoff),
    ).fetchall()

    click.echo(f"\n  Upcoming deadlines (next {days} days): {len(rows)}\n")
    _divider()

    for r in rows:
        dl = date.fromisoformat(r["deadline_date"])
        days_left = (dl - today).days
        urgency = "🔴 CRITICAL" if days_left <= 14 else "🟠 HIGH" if days_left <= 30 else "🟡 MEDIUM"
        click.echo(f"  {urgency}  {r['deadline_date']}  ({days_left}d)  [{r['agency'] or 'N/A'}]")
        click.echo(f"            {r['title'][:70]}")
        click.echo()

    conn.close()


if __name__ == "__main__":
    cli()
