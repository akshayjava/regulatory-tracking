import sqlite3
import pytest
from backend.ingestion.deduplication import is_duplicate

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE regulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regulation_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            source TEXT NOT NULL
        )
    """)

    # Insert some seed data
    cur.execute(
        "INSERT INTO regulations (regulation_id, title, source) VALUES (?, ?, ?)",
        ("reg_123", "The Very Important Regulation on Data Privacy", "congress")
    )
    cur.execute(
        "INSERT INTO regulations (regulation_id, title, source) VALUES (?, ?, ?)",
        ("reg_456", "Guidance on Crypto Custody", "sec")
    )
    conn.commit()

    yield conn
    conn.close()

def test_is_duplicate_exact_id_match(db_conn):
    reg = {"regulation_id": "reg_123", "title": "Some Different Title", "source": "congress"}
    assert is_duplicate(reg, db_conn) is True

def test_is_duplicate_title_similarity_match(db_conn):
    # Same source, very similar title, different ID
    # 7 words overlap, 8 words max -> 7/8 = 0.875 > 0.85
    reg = {
        "regulation_id": "reg_789",
        "title": "The Very Important Regulation on Data Privacy Rules",
        "source": "congress"
    }
    assert is_duplicate(reg, db_conn) is True

def test_is_duplicate_no_match(db_conn):
    reg = {
        "regulation_id": "reg_999",
        "title": "Unrelated Healthcare Rule",
        "source": "cms"
    }
    assert is_duplicate(reg, db_conn) is False

def test_is_duplicate_title_similarity_different_source(db_conn):
    # Even with same title, if the source is different, it shouldn't match
    reg = {
        "regulation_id": "reg_789",
        "title": "The Very Important Regulation on Data Privacy Rules",
        "source": "sec" # different source than 'congress'
    }
    assert is_duplicate(reg, db_conn) is False

def test_is_duplicate_empty_regulation(db_conn):
    reg = {}
    assert is_duplicate(reg, db_conn) is False
