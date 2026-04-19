import os
import sqlite3
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# We need to set the DB_PATH environment variable before importing the app or database modules.
@pytest.fixture(scope="session", autouse=True)
def setup_test_db_env():
    # Create a temporary file for the database
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Set the environment variable used by backend.api.database
    os.environ["DB_PATH"] = path

    # We must also mock backend.api.database.DB_PATH directly because it is initialized at import time
    import backend.api.database
    backend.api.database.DB_PATH = path

    yield path

    # Cleanup after tests
    os.remove(path)


@pytest.fixture(scope="function", autouse=True)
def init_test_db(setup_test_db_env):
    """
    Initializes the database schema for each test.
    We drop all tables and recreate them to ensure a clean state.
    """
    db_path = setup_test_db_env
    schema_path = Path(__file__).parent.parent / "db" / "schema.sql"

    with sqlite3.connect(db_path) as conn:
        # Clear existing tables (optional, but good for test isolation if using file DB)
        # Using schema.sql is sufficient if it's an empty DB, but if tests run sequentially,
        # we might want to clear it. For now, since schema.sql uses "CREATE TABLE IF NOT EXISTS",
        # let's just delete the file content or run schema.
        pass

    # Since sqlite script might not run successfully, let's just wipe tables
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = OFF;")
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        for table in tables:
            if table[0] != "sqlite_sequence":
                conn.execute(f"DROP TABLE IF EXISTS {table[0]};")
        conn.execute("PRAGMA foreign_keys = ON;")

        # Now init schema
        conn.executescript(schema_path.read_text())
        conn.commit()


@pytest.fixture
def client():
    # Import inside fixture to ensure env vars are set
    from backend.api.main import app
    return TestClient(app)
