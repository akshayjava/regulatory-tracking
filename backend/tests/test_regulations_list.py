import pytest
import sqlite3

@pytest.fixture
def sample_data(setup_test_db):
    db_path = setup_test_db
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        # Insert Agency
        conn.execute("INSERT INTO agencies (id, name, abbreviation) VALUES (1, 'Securities and Exchange Commission', 'SEC')")
        conn.execute("INSERT INTO agencies (id, name, abbreviation) VALUES (2, 'Food and Drug Administration', 'FDA')")

        # Insert Regulations
        # Reg 1: Crypto, Proposed, SEC, matching search "bitcoin"
        conn.execute("""
            INSERT INTO regulations (id, regulation_id, title, type, status, source, summary, agency_id, impact_score)
            VALUES (1, 'reg-1', 'Bitcoin ETF Proposal', 'rule', 'proposed', 'sec', 'Rules for bitcoin ETFs', 1, 8)
        """)
        conn.execute("INSERT INTO regulation_verticals (regulation_id, vertical, relevance_score, is_critical) VALUES (1, 'crypto', 5, 0)")

        # Reg 2: Healthcare, Effective, FDA, matching search "device"
        conn.execute("""
            INSERT INTO regulations (id, regulation_id, title, type, status, source, summary, agency_id, impact_score)
            VALUES (2, 'reg-2', 'Medical Device Tracking', 'rule', 'effective', 'fda', 'Tracking medical devices', 2, 7)
        """)
        conn.execute("INSERT INTO regulation_verticals (regulation_id, vertical, relevance_score, is_critical) VALUES (2, 'healthcare', 7, 1)")

        # Reg 3: Crypto, Final, SEC, deadline approaching
        conn.execute("""
            INSERT INTO regulations (id, regulation_id, title, type, status, source, summary, agency_id, impact_score, deadline_date)
            VALUES (3, 'reg-3', 'Stablecoin Reporting', 'rule', 'final', 'sec', 'Reporting for stablecoins', 1, 9, date('now', '+15 days'))
        """)
        conn.execute("INSERT INTO regulation_verticals (regulation_id, vertical, relevance_score, is_critical) VALUES (3, 'crypto', 9, 1)")

        # Reg 4: Fintech, Withdrawn, no agency
        conn.execute("""
            INSERT INTO regulations (id, regulation_id, title, type, status, source, summary, impact_score)
            VALUES (4, 'reg-4', 'P2P Lending Rules', 'guidance', 'withdrawn', 'state', 'P2P lending rules', 5)
        """)
        conn.execute("INSERT INTO regulation_verticals (regulation_id, vertical, relevance_score, is_critical) VALUES (4, 'fintech', 3, 0)")

        conn.commit()

def test_list_all_regulations(client, sample_data):
    response = client.get("/regulations/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert len(data["items"]) == 4
    # Order should be by impact_score DESC: 3, 1, 2, 4
    assert data["items"][0]["regulation_id"] == "reg-3"
    assert data["items"][1]["regulation_id"] == "reg-1"

def test_filter_by_vertical(client, sample_data):
    response = client.get("/regulations/?vertical=crypto")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    ids = [item["regulation_id"] for item in data["items"]]
    assert "reg-1" in ids
    assert "reg-3" in ids

def test_filter_by_status(client, sample_data):
    response = client.get("/regulations/?status=proposed")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["regulation_id"] == "reg-1"

def test_filter_by_agency(client, sample_data):
    response = client.get("/regulations/?agency=SEC")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    ids = [item["regulation_id"] for item in data["items"]]
    assert "reg-1" in ids
    assert "reg-3" in ids

def test_search(client, sample_data):
    response = client.get("/regulations/?search=bitcoin")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["regulation_id"] == "reg-1"

def test_filter_deadline(client, sample_data):
    response = client.get("/regulations/?deadline_within_days=30")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["regulation_id"] == "reg-3"

def test_pagination(client, sample_data):
    response = client.get("/regulations/?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert len(data["items"]) == 2
    assert data["items"][0]["regulation_id"] == "reg-3"
    assert data["items"][1]["regulation_id"] == "reg-1"

    response2 = client.get("/regulations/?page=2&page_size=2")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["items"]) == 2
    assert data2["items"][0]["regulation_id"] == "reg-2"
    assert data2["items"][1]["regulation_id"] == "reg-4"

def test_invalid_vertical(client):
    response = client.get("/regulations/?vertical=invalid_vert")
    assert response.status_code == 400
    assert "Invalid vertical" in response.json()["detail"]

def test_invalid_status(client):
    response = client.get("/regulations/?status=invalid_stat")
    assert response.status_code == 400
    assert "Invalid status" in response.json()["detail"]

def test_combination_filters(client, sample_data):
    response = client.get("/regulations/?vertical=crypto&status=proposed&agency=SEC")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["regulation_id"] == "reg-1"

    # Search + Deadline
    response2 = client.get("/regulations/?search=stablecoin&deadline_within_days=30")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["total"] == 1
    assert data2["items"][0]["regulation_id"] == "reg-3"

    # Search with no results
    response3 = client.get("/regulations/?search=notfound")
    assert response3.status_code == 200
    assert response3.json()["total"] == 0
