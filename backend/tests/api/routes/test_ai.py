import os
import sqlite3
from unittest.mock import MagicMock, patch

import pytest

from backend.api.database import DB_PATH

# We use the DB_PATH from environment, which is set in conftest.py
import backend.api.database

def test_annotate_regulation_not_found(client):
    response = client.post("/ai/annotate/non_existent_reg")
    assert response.status_code == 404
    assert response.json()["detail"] == "Regulation not found"

def test_get_annotation_not_found(client):
    # Test DB is empty initially due to init_test_db
    response = client.get("/ai/annotation/non_existent_reg")
    assert response.status_code == 404

def test_annotate_regulation_success(client):
    # Insert a fake regulation directly into DB to test
    with sqlite3.connect(backend.api.database.DB_PATH) as conn:
        conn.execute("""
            INSERT INTO regulations (regulation_id, title, type, status, source)
            VALUES (?, ?, ?, ?, ?)
        """, ("REG-123", "Test Regulation", "rule", "final", "congress"))
        conn.commit()
        row = conn.execute("SELECT id FROM regulations WHERE regulation_id = 'REG-123'").fetchone()
        reg_id = row[0]

    # Mock the Anthropic client
    mock_client_instance = MagicMock()
    mock_response = MagicMock()
    mock_text_block = MagicMock()
    mock_text_block.type = "text"
    mock_text_block.text = "This is a mock AI plain-language annotation."
    mock_response.content = [mock_text_block]
    mock_client_instance.messages.create.return_value = mock_response

    with patch("backend.api.routes.ai._get_client", return_value=mock_client_instance):
        # 1. Test Generate Annotation
        response = client.post("/ai/annotate/REG-123")
        assert response.status_code == 200
        data = response.json()
        assert data["regulation_id"] == "REG-123"
        assert data["title"] == "Test Regulation"
        assert data["annotation"] == "This is a mock AI plain-language annotation."
        assert data["cached"] is False
        assert data["model_used"] == "claude-opus-4-6"

        # Check DB cache
        with sqlite3.connect(backend.api.database.DB_PATH) as conn:
            cached = conn.execute(
                "SELECT annotation, model_used FROM regulation_annotations WHERE regulation_id=?",
                (reg_id,)
            ).fetchone()
            assert cached is not None
            assert cached[0] == "This is a mock AI plain-language annotation."
            assert cached[1] == "claude-opus-4-6"

        # 2. Test Cache Retrieval
        mock_client_instance.messages.create.reset_mock()
        response_cached = client.post("/ai/annotate/REG-123")
        assert response_cached.status_code == 200
        data_cached = response_cached.json()
        assert data_cached["cached"] is True
        assert data_cached["annotation"] == "This is a mock AI plain-language annotation."
        # Verify AI client was NOT called
        mock_client_instance.messages.create.assert_not_called()

        # 3. Test GET Annotation
        response_get = client.get("/ai/annotation/REG-123")
        assert response_get.status_code == 200
        assert response_get.json()["cached"] is True
        assert response_get.json()["annotation"] == "This is a mock AI plain-language annotation."

        # 4. Test Force Refresh
        # Change the mock response to simulate a new answer
        mock_text_block_2 = MagicMock()
        mock_text_block_2.type = "text"
        mock_text_block_2.text = "This is an UPDATED mock annotation."
        mock_response_2 = MagicMock()
        mock_response_2.content = [mock_text_block_2]
        mock_client_instance.messages.create.return_value = mock_response_2

        response_refresh = client.post("/ai/annotate/REG-123?force_refresh=true")
        assert response_refresh.status_code == 200
        data_refresh = response_refresh.json()
        assert data_refresh["cached"] is False
        assert data_refresh["annotation"] == "This is an UPDATED mock annotation."
        mock_client_instance.messages.create.assert_called_once()

        # Verify DB is updated
        with sqlite3.connect(backend.api.database.DB_PATH) as conn:
            cached_updated = conn.execute(
                "SELECT annotation FROM regulation_annotations WHERE regulation_id=?",
                (reg_id,)
            ).fetchone()
            assert cached_updated[0] == "This is an UPDATED mock annotation."

def test_get_annotation_without_cache(client):
    # Insert a fake regulation, but NO cache
    with sqlite3.connect(backend.api.database.DB_PATH) as conn:
        conn.execute("""
            INSERT INTO regulations (regulation_id, title, type, status, source)
            VALUES (?, ?, ?, ?, ?)
        """, ("REG-NO-CACHE", "No Cache Reg", "rule", "final", "congress"))
        conn.commit()

    response = client.get("/ai/annotation/REG-NO-CACHE")
    assert response.status_code == 404
    assert response.json()["detail"] == "No annotation yet — call POST /ai/annotate/{id} to generate one"
