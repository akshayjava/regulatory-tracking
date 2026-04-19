import os
import tempfile
import sqlite3
import pytest
from fastapi.testclient import TestClient

# Mock DB_PATH before importing app so it uses the temporary DB
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    db_fd, db_path = tempfile.mkstemp()

    # Store original and set new
    original_db = os.environ.get("DB_PATH")
    os.environ["DB_PATH"] = db_path

    # Needs to be imported after setting DB_PATH so it reads the env var correctly
    import api.database as db
    db.DB_PATH = db_path

    db.init_db()

    yield db_path

    os.close(db_fd)
    os.unlink(db_path)
    if original_db is not None:
        os.environ["DB_PATH"] = original_db
    else:
        del os.environ["DB_PATH"]

@pytest.fixture(scope="session")
def client():
    # Import app here so the test DB is fully set up before app initializes
    from api.main import app
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def clean_db(setup_test_db):
    db_path = setup_test_db
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = OFF;")
        # Dynamically clear all user tables
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
        for row in cursor.fetchall():
            conn.execute(f"DELETE FROM {row[0]}")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
