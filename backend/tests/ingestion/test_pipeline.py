import os
import sqlite3
import pytest

from backend.ingestion.pipeline import IngestionPipeline

@pytest.fixture
def test_db_path(tmp_path):
    db_file = tmp_path / "test_pipeline.db"
    return str(db_file)

@pytest.fixture
def pipeline(test_db_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", test_db_path)
    # create the schema in the test database
    conn = sqlite3.connect(test_db_path)
    schema_path = os.path.join(os.path.dirname(__file__), "..", "..", "db", "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path) as f:
            conn.executescript(f.read())
        conn.commit()
    conn.close()

    return IngestionPipeline(db_path=test_db_path)

def test_save_regulation_new_insert(pipeline):
    conn = pipeline._get_conn()
    reg = {
        "regulation_id": "test-reg-1",
        "title": "Test Regulation 1",
        "type": "bill",
        "status": "proposed",
        "source": "congress",
        "agency": "TEST",
        "verticals": [("fintech", 8, True)]
    }

    result = pipeline._save_regulation(conn, reg)
    assert result == "new"

    # Verify records were inserted
    cur = conn.cursor()
    row = cur.execute("SELECT id, title, agency_id FROM regulations WHERE regulation_id = 'test-reg-1'").fetchone()
    assert row is not None
    assert row["title"] == "Test Regulation 1"

    # Verify agency
    agency = cur.execute("SELECT name FROM agencies WHERE id = ?", (row["agency_id"],)).fetchone()
    assert agency is not None
    assert agency["name"] == "TEST"

    # Verify verticals
    vertical = cur.execute("SELECT vertical, relevance_score, is_critical FROM regulation_verticals WHERE regulation_id = ?", (row["id"],)).fetchone()
    assert vertical is not None
    assert vertical["vertical"] == "fintech"
    assert vertical["relevance_score"] == 8
    assert vertical["is_critical"] == 1

    # Verify update
    update = cur.execute("SELECT update_type, urgency FROM regulation_updates WHERE regulation_id = ?", (row["id"],)).fetchone()
    assert update is not None
    assert update["update_type"] == "new_regulation"

    conn.close()

def test_save_regulation_update(pipeline):
    conn = pipeline._get_conn()
    reg = {
        "regulation_id": "test-reg-2",
        "title": "Test Regulation 2",
        "type": "bill",
        "status": "proposed",
        "source": "congress",
        "agency": "TEST"
    }

    # First insert should be "new"
    result1 = pipeline._save_regulation(conn, reg)
    assert result1 == "new"

    # Change status and deadline_date
    reg["status"] = "final"
    reg["deadline_date"] = "2024-12-31"

    # Mock is_duplicate to return False so it updates
    import backend.ingestion.pipeline as pipeline_mod
    import types
    original_is_duplicate = pipeline_mod.is_duplicate
    try:
        pipeline_mod.is_duplicate = lambda r, c: False

        # Second save with same regulation_id should update
        result2 = pipeline._save_regulation(conn, reg)
        assert result2 == "updated"
    finally:
        pipeline_mod.is_duplicate = original_is_duplicate

    cur = conn.cursor()
    row = cur.execute("SELECT status, deadline_date FROM regulations WHERE regulation_id = 'test-reg-2'").fetchone()
    assert row is not None
    assert row["status"] == "final"
    assert row["deadline_date"] == "2024-12-31"

    conn.close()

def test_save_regulation_skipped(pipeline, monkeypatch):
    # Mock is_duplicate to always return True
    import backend.ingestion.pipeline as pipeline_mod
    monkeypatch.setattr(pipeline_mod, "is_duplicate", lambda r, c: True)

    conn = pipeline._get_conn()
    reg = {
        "regulation_id": "test-reg-3",
        "title": "Test Regulation 3"
    }

    result = pipeline._save_regulation(conn, reg)
    assert result == "skipped"
    conn.close()
