import json
import sqlite3
import pytest

from api.database import row_to_dict

def get_row_from_data(data_dict):
    """Helper to create a sqlite3.Row from a dictionary using an in-memory DB."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # Create a table dynamically based on keys
    columns = ", ".join(f"{k} TEXT" for k in data_dict.keys())
    conn.execute(f"CREATE TABLE test_table ({columns})")

    # Insert the data
    placeholders = ", ".join("?" for _ in data_dict.keys())
    conn.execute(f"INSERT INTO test_table VALUES ({placeholders})", tuple(data_dict.values()))

    # Fetch the row
    row = conn.execute("SELECT * FROM test_table").fetchone()
    conn.close()

    return row

def test_row_to_dict_valid_json():
    # Test valid JSON strings in fields that should be parsed
    data = {
        "affected_entities": '["Bank A", "Bank B"]',
        "keywords": '["finance", "compliance"]',
        "compliance_requirements": '{"req1": "must do A", "req2": "must do B"}',
        "details": '{"version": 1, "status": "active"}',
        "other_field": "just a string"
    }
    row = get_row_from_data(data)
    result = row_to_dict(row)

    assert result["affected_entities"] == ["Bank A", "Bank B"]
    assert result["keywords"] == ["finance", "compliance"]
    assert result["compliance_requirements"] == {"req1": "must do A", "req2": "must do B"}
    assert result["details"] == {"version": 1, "status": "active"}
    assert result["other_field"] == "just a string"

def test_row_to_dict_invalid_json():
    # Test invalid JSON strings in fields that should be parsed
    data = {
        "affected_entities": '["Bank A", "Bank B"', # Missing closing bracket
        "keywords": 'invalid json',
    }
    row = get_row_from_data(data)
    result = row_to_dict(row)

    # Should fall back to the original string
    assert result["affected_entities"] == '["Bank A", "Bank B"'
    assert result["keywords"] == 'invalid json'

def test_row_to_dict_non_string():
    # Test non-string values in fields that should be parsed
    # sqlite3 in memory allows us to insert numbers even if declared as TEXT or we can skip type declaration
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE test_table (affected_entities INTEGER, keywords REAL)")
    conn.execute("INSERT INTO test_table VALUES (123, 45.6)")
    row = conn.execute("SELECT * FROM test_table").fetchone()
    conn.close()

    result = row_to_dict(row)

    # Non-strings should be unchanged
    assert result["affected_entities"] == 123
    assert result["keywords"] == 45.6

def test_row_to_dict_other_json_fields_ignored():
    # Test valid JSON in fields that are NOT in the special list
    data = {
        "not_a_special_field": '{"key": "value"}',
        "another_field": '[1, 2, 3]'
    }
    row = get_row_from_data(data)
    result = row_to_dict(row)

    # These should remain as strings, not parsed
    assert result["not_a_special_field"] == '{"key": "value"}'
    assert result["another_field"] == '[1, 2, 3]'

def test_row_to_dict_empty_fields():
    # Test when fields are not present or None
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE test_table (id INTEGER, affected_entities TEXT)")
    conn.execute("INSERT INTO test_table VALUES (1, NULL)")
    row = conn.execute("SELECT * FROM test_table").fetchone()
    conn.close()

    result = row_to_dict(row)

    assert result["id"] == 1
    assert result["affected_entities"] is None
