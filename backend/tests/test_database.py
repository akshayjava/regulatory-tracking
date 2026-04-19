import pytest
import sqlite3
from unittest.mock import patch, MagicMock

from api.database import get_regulation_count

@pytest.fixture
def memory_db():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE regulations (id INTEGER PRIMARY KEY, title TEXT)"
    )
    conn.commit()

    with patch("api.database.get_db") as mock_get_db:
        # get_db is a context manager yielding the connection
        mock_get_db.return_value.__enter__.return_value = conn
        yield conn
    conn.close()

def test_get_regulation_count_empty(memory_db):
    assert get_regulation_count() == 0

def test_get_regulation_count_with_records(memory_db):
    memory_db.execute("INSERT INTO regulations (title) VALUES ('Reg 1')")
    memory_db.execute("INSERT INTO regulations (title) VALUES ('Reg 2')")
    memory_db.commit()
    assert get_regulation_count() == 2

def test_get_regulation_count_none_row():
    # Test the fallback logic if row is somehow None
    with patch("api.database.get_db") as mock_get_db:
        mock_conn = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_conn

        mock_cursor = MagicMock()
        # Mock fetchone to return None
        mock_cursor.fetchone.return_value = None
        mock_conn.execute.return_value = mock_cursor

        assert get_regulation_count() == 0
