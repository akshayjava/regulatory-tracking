import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

def test_alerts_deadlines_urgency(client: TestClient, db_conn):
    today = date.today()

    # Clean up existing data for test isolation
    db_conn.execute("DELETE FROM regulations")
    db_conn.execute("DELETE FROM regulation_verticals")

    # Create regulations with different deadlines
    deadlines = [
        # critical: <= 14 days
        (today + timedelta(days=5)).isoformat(),
        (today + timedelta(days=14)).isoformat(),
        # high: <= 30 days
        (today + timedelta(days=15)).isoformat(),
        (today + timedelta(days=30)).isoformat(),
        # medium: > 30 days
        (today + timedelta(days=31)).isoformat(),
        (today + timedelta(days=60)).isoformat(),
    ]

    regs_to_insert = []
    for i, dl in enumerate(deadlines):
        reg_id = f"test-reg-{i}"
        regs_to_insert.append((
            reg_id,
            f"Test Regulation {i}",
            "rule",
            "proposed",
            "sec",
            dl,
            5
        ))

    db_conn.executemany(
        """INSERT INTO regulations
           (regulation_id, title, type, status, source, deadline_date, impact_score)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        regs_to_insert
    )
    db_conn.commit()

    # Call the endpoint
    response = client.get("/alerts/deadlines?days=90")
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 6

    # Sort results by deadline to ensure predictable matching
    results.sort(key=lambda x: x["deadline_date"])

    # Verify exact urgencies based on the calculated deadlines
    assert results[0]["urgency"] == "critical" # 5 days
    assert results[1]["urgency"] == "critical" # 14 days
    assert results[2]["urgency"] == "high"     # 15 days
    assert results[3]["urgency"] == "high"     # 30 days
    assert results[4]["urgency"] == "medium"   # 31 days
    assert results[5]["urgency"] == "medium"   # 60 days
