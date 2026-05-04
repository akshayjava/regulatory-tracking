import pytest
import sqlite3
from datetime import datetime, timedelta

@pytest.fixture
def mock_datetime(mocker):
    # Mock datetime.utcnow() to return a fixed time
    fixed_now = datetime(2023, 10, 10, 12, 0, 0)
    mock_dt = mocker.patch("api.routes.alerts.datetime")
    mock_dt.utcnow.return_value = fixed_now
    mock_dt.now.return_value = fixed_now
    # Need to keep other attributes of datetime working
    mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
    return fixed_now

@pytest.fixture
def alerts_sample_data(setup_test_db, mock_datetime):
    db_path = setup_test_db
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        now = mock_datetime

        # Insert Agencies
        conn.execute("INSERT OR IGNORE INTO agencies (id, name, abbreviation) VALUES (1, 'Securities and Exchange Commission', 'SEC')")

        # Reg 1: Just created (5 hours ago)
        created_5h = (now - timedelta(hours=5)).isoformat()
        conn.execute(f"""
            INSERT INTO regulations (id, regulation_id, title, type, status, source, impact_score, created_at)
            VALUES (10, 'reg-new-1', 'Very New Rule', 'rule', 'proposed', 'sec', 8, '{created_5h}')
        """)

        # Reg 2: Created 20 hours ago
        created_20h = (now - timedelta(hours=20)).isoformat()
        conn.execute(f"""
            INSERT INTO regulations (id, regulation_id, title, type, status, source, impact_score, created_at)
            VALUES (11, 'reg-new-2', 'Newish Rule', 'rule', 'proposed', 'sec', 7, '{created_20h}')
        """)

        # Reg 3: Created 30 hours ago
        created_30h = (now - timedelta(hours=30)).isoformat()
        conn.execute(f"""
            INSERT INTO regulations (id, regulation_id, title, type, status, source, impact_score, created_at)
            VALUES (12, 'reg-old-1', 'Old Rule', 'rule', 'proposed', 'sec', 6, '{created_30h}')
        """)

        # Reg 4: Created 50 hours ago
        created_50h = (now - timedelta(hours=50)).isoformat()
        conn.execute(f"""
            INSERT INTO regulations (id, regulation_id, title, type, status, source, impact_score, created_at)
            VALUES (13, 'reg-old-2', 'Older Rule', 'rule', 'proposed', 'sec', 5, '{created_50h}')
        """)

        conn.commit()

def test_get_new_regulations_default_24h(client, alerts_sample_data):
    response = client.get("/alerts/new")
    assert response.status_code == 200
    data = response.json()

    # Should only return regulations created within the last 24 hours
    assert len(data) == 2

    # Ordered by created_at DESC, so the newest should be first
    assert data[0]["regulation_id"] == "reg-new-1"
    assert data[1]["regulation_id"] == "reg-new-2"

def test_get_new_regulations_custom_48h(client, alerts_sample_data):
    response = client.get("/alerts/new?hours=48")
    assert response.status_code == 200
    data = response.json()

    # Should return regulations created within the last 48 hours
    assert len(data) == 3

    assert data[0]["regulation_id"] == "reg-new-1"
    assert data[1]["regulation_id"] == "reg-new-2"
    assert data[2]["regulation_id"] == "reg-old-1"

def test_get_new_regulations_invalid_hours_low(client):
    response = client.get("/alerts/new?hours=0")
    assert response.status_code == 422
    data = response.json()
    # Check that it's a validation error
    assert "detail" in data

def test_get_new_regulations_invalid_hours_high(client):
    response = client.get("/alerts/new?hours=200")
    assert response.status_code == 422
    data = response.json()
    # Check that it's a validation error
    assert "detail" in data
