import sqlite3
from datetime import date

def seed():
    conn = sqlite3.connect("backend/lattice.db")
    cur = conn.cursor()
    for i in range(1000):
        cur.execute(
            """INSERT INTO regulations
               (regulation_id, title, type, status, source, summary,
                published_date, effective_date, deadline_date,
                complexity_score, impact_score, affected_entities, keywords, citation, agency_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                f"reg-{i}", f"Title {i}", "rule", "effective", "congress", "Summary",
                str(date.today()), str(date.today()), str(date.today()),
                5, 5, "[]", "[]", "Citation", 1
            )
        )
        reg_id = cur.lastrowid
        cur.execute(
            "INSERT INTO regulation_verticals (regulation_id, vertical, relevance_score, is_critical) VALUES (?,?,?,?)",
            (reg_id, "crypto", 10, 1)
        )
    conn.commit()
    conn.close()

seed()
