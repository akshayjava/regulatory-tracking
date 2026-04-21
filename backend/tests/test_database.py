import sqlite3
import pytest
from unittest.mock import patch, MagicMock

from backend.api.database import get_regulation_count

@pytest.fixture
def mock_db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE regulations (id INTEGER PRIMARY KEY, title TEXT)")
    yield conn
    conn.close()

def test_get_regulation_count_empty(mock_db_conn):
    with patch("backend.api.database.get_db") as mock_get_db:
        mock_get_db.return_value.__enter__.return_value = mock_db_conn

        count = get_regulation_count()
        assert count == 0

def test_get_regulation_count_with_records(mock_db_conn):
    mock_db_conn.execute("INSERT INTO regulations (title) VALUES ('Reg 1'), ('Reg 2'), ('Reg 3')")
    mock_db_conn.commit()

    with patch("backend.api.database.get_db") as mock_get_db:
        mock_get_db.return_value.__enter__.return_value = mock_db_conn

        count = get_regulation_count()
        assert count == 3

def test_get_regulation_count_no_row():
    with patch("backend.api.database.get_db") as mock_get_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.execute.return_value = mock_cursor
        mock_get_db.return_value.__enter__.return_value = mock_conn

        count = get_regulation_count()
        assert count == 0
