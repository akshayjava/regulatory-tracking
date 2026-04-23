import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from backend.api.main import app

client = TestClient(app)

def test_ai_query_invalid_vertical():
    response = client.post(
        "/ai/query",
        json={"question": "What are the rules?", "vertical": "invalid_vertical", "stream": False}
    )
    assert response.status_code == 400
    assert "Invalid vertical. Valid:" in response.json()["detail"]

def test_ai_query_valid_vertical_mocked(mocker):
    # Mock the database connection
    mock_db = MagicMock()
    mock_conn = MagicMock()
    mock_db.__enter__.return_value = mock_conn
    mocker.patch("backend.api.routes.ai.get_db", return_value=mock_db)

    # Mock the fetch context to avoid executing sql
    mocker.patch("backend.api.routes.ai._fetch_regulations_context", return_value="mock context")

    # Mock the anthropic client
    mock_anthropic = MagicMock()
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client

    # Setup mock response for non-streamed request
    mock_response = MagicMock()
    mock_text_block = MagicMock()
    mock_text_block.type = "text"
    mock_text_block.text = "This is a mock answer."
    mock_response.content = [mock_text_block]
    mock_client.messages.create.return_value = mock_response

    mocker.patch("backend.api.routes.ai._get_client", return_value=mock_client)

    response = client.post(
        "/ai/query",
        json={"question": "What are the rules?", "vertical": "crypto", "stream": False}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is a mock answer."
    assert "model" in data

    # Verify that the anthropic client was called
    mock_client.messages.create.assert_called_once()

    # Also verify without vertical
    response_no_vertical = client.post(
        "/ai/query",
        json={"question": "What are the rules?", "stream": False}
    )

    assert response_no_vertical.status_code == 200
    assert response_no_vertical.json()["answer"] == "This is a mock answer."
