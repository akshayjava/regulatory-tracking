
def test_ai_query_stream(client, mocker):
    mock_client = mocker.MagicMock()
    mock_stream = mocker.MagicMock()

    # Mock stream response
    mock_stream.__enter__.return_value.text_stream = ["This ", "is ", "a ", "test ", "response."]
    mock_client.messages.stream.return_value = mock_stream

    mocker.patch("api.routes.ai._get_client", return_value=mock_client)

    response = client.post("/ai/query", json={"question": "What is the meaning of life?", "stream": True})

    assert response.status_code == 200
    assert response.text == "This is a test response."

def test_ai_query_no_stream(client, mocker):
    mock_client = mocker.MagicMock()
    mock_response = mocker.MagicMock()

    mock_block = mocker.MagicMock()
    mock_block.type = "text"
    mock_block.text = "This is a non-streamed response."

    mock_response.content = [mock_block]
    mock_client.messages.create.return_value = mock_response

    mocker.patch("api.routes.ai._get_client", return_value=mock_client)

    response = client.post("/ai/query", json={"question": "What is the meaning of life?", "stream": False})

    assert response.status_code == 200
    assert response.json() == {"answer": "This is a non-streamed response.", "model": "claude-opus-4-6"}

def test_ai_query_invalid_vertical(client):
    response = client.post("/ai/query", json={"question": "What?", "vertical": "invalid_vertical"})
    assert response.status_code == 400
    assert "Invalid vertical" in response.json()["detail"]

def test_ai_query_missing_api_key(client, monkeypatch):
    # Ensure ANTHROPIC_API_KEY is not set
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    response = client.post("/ai/query", json={"question": "Test missing API key"})
    assert response.status_code == 500
    assert "ANTHROPIC_API_KEY not configured" in response.json()["detail"]

def test_ai_query_valid_vertical(client, mocker):
    mock_client = mocker.MagicMock()
    mock_response = mocker.MagicMock()

    mock_block = mocker.MagicMock()
    mock_block.type = "text"
    mock_block.text = "Valid vertical response."

    mock_response.content = [mock_block]
    mock_client.messages.create.return_value = mock_response

    mocker.patch("api.routes.ai._get_client", return_value=mock_client)
    mock_fetch_context = mocker.patch("api.routes.ai._fetch_regulations_context", return_value="Test context")

    response = client.post("/ai/query", json={"question": "What?", "vertical": "crypto", "stream": False})

    assert response.status_code == 200
    assert response.json() == {"answer": "Valid vertical response.", "model": "claude-opus-4-6"}

    # Check that _fetch_regulations_context was called with the correct vertical
    assert mock_fetch_context.call_args[0][1] == "crypto"
