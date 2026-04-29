from datetime import date, datetime, timedelta
import pytest

from api.database import get_db

@pytest.fixture
def alerts_sample_data(db_conn):
    today = date.today()
    now = datetime.utcnow()

    # Agency
    db_conn.execute("INSERT INTO agencies (name, abbreviation) VALUES ('SEC', 'SEC')")
    agency_id = db_conn.execute("SELECT id FROM agencies WHERE abbreviation='SEC'").fetchone()[0]

    # Regulations
    regs = [
        ("REG-DEADLINE-1", "Upcoming Deadline 1", "proposed", today + timedelta(days=10), now), # Critical
        ("REG-DEADLINE-2", "Upcoming Deadline 2", "proposed", today + timedelta(days=25), now), # High
        ("REG-DEADLINE-3", "Upcoming Deadline 3", "proposed", today + timedelta(days=40), now), # Medium
        ("REG-DEADLINE-4", "Far Deadline", "proposed", today + timedelta(days=100), now),
        ("REG-NEW-1", "Brand New 1", "effective", today + timedelta(days=5), now - timedelta(hours=2)),
        ("REG-NEW-2", "Brand New 2", "effective", today + timedelta(days=5), now - timedelta(hours=12)),
        ("REG-NEW-3", "Recent 3", "effective", today + timedelta(days=5), now - timedelta(hours=36)),
        ("REG-OLD", "Old Regulation", "effective", today + timedelta(days=5), now - timedelta(hours=100)),
    ]

    for reg_id, title, status, deadline, created in regs:
        db_conn.execute(
            """INSERT INTO regulations (regulation_id, title, type, status, source, impact_score, deadline_date, created_at, agency_id)
               VALUES (?, ?, 'rule', ?, 'sec', 8, ?, ?, ?)""",
            (reg_id, title, status, str(deadline), created.isoformat(), agency_id)
        )

    db_conn.commit()

    # Verticals
    # We'll attach crypto to some of the deadline ones
    for reg_id in ["REG-DEADLINE-1", "REG-DEADLINE-2"]:
        r_id = db_conn.execute("SELECT id FROM regulations WHERE regulation_id=?", (reg_id,)).fetchone()[0]
        db_conn.execute("INSERT INTO regulation_verticals (regulation_id, vertical) VALUES (?, 'crypto')", (r_id,))

    db_conn.commit()

    yield

    # Teardown
    db_conn.execute("DELETE FROM regulation_verticals")
    db_conn.execute("DELETE FROM regulations")
    db_conn.execute("DELETE FROM agencies")
    db_conn.commit()

def test_get_deadlines(client, alerts_sample_data):
    response = client.get("/alerts/deadlines?days=30")
    assert response.status_code == 200
    data = response.json()

    # Should only return deadline 1 and 2 (within 30 days) + the 3 new ones that have default deadline of 5 days
    assert len(data) == 6

def test_get_new_regulations_default_24h(client, alerts_sample_data):
    response = client.get("/alerts/new")
    assert response.status_code == 200
    data = response.json()

    # Should only return regulations created within the last 24 hours
    assert len(data) == 6

def test_get_new_regulations_custom_48h(client, alerts_sample_data):
    response = client.get("/alerts/new?hours=48")
    assert response.status_code == 200
    data = response.json()

    # Should return regulations created within the last 48 hours
    assert len(data) == 7

def test_get_critical_alerts(client, alerts_sample_data, db_conn):
    # Setup some updates
    r_id = db_conn.execute("SELECT id FROM regulations WHERE regulation_id='REG-DEADLINE-1'").fetchone()[0]

    db_conn.execute(
        """INSERT INTO regulation_updates (regulation_id, update_type, urgency, details)
           VALUES (?, 'status_change', 'critical', 'Test detail')""",
        (r_id,)
    )
    db_conn.commit()

    response = client.get("/alerts/critical")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["urgency"] == "critical"
    assert data[0]["regulation_id"] == "REG-DEADLINE-1"
