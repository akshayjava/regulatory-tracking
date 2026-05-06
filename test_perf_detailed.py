import time
import sqlite3

base_url = "http://localhost:8000"

def get_db():
    conn = sqlite3.connect("backend/lattice.db")
    conn.row_factory = sqlite3.Row
    return conn

def slow_way():
    conn = get_db()
    rows = conn.execute("SELECT * FROM regulations LIMIT 1000").fetchall()
    start = time.time()
    for row in rows:
        reg_id = row["id"]
        cur = conn.execute(
            "SELECT vertical, relevance_score, is_critical FROM regulation_verticals WHERE regulation_id=?",
            (reg_id,),
        )
        verticals = cur.fetchall()
    return time.time() - start

def fast_way():
    conn = get_db()
    rows = conn.execute("SELECT * FROM regulations LIMIT 1000").fetchall()
    start = time.time()
    ids = [r["id"] for r in rows]
    placeholders = ",".join(["?"] * len(ids))
    cur = conn.execute(
        f"SELECT regulation_id, vertical, relevance_score, is_critical FROM regulation_verticals WHERE regulation_id IN ({placeholders})",
        ids,
    )
    all_verticals = cur.fetchall()
    v_map = {}
    for r in all_verticals:
        v_map.setdefault(r["regulation_id"], []).append(r)
    return time.time() - start

if __name__ == "__main__":
    print("Slow way:", slow_way())
    print("Fast way:", fast_way())
