from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_trigger_sync_invalid_source():
    response = client.post("/sources/sync/invalid_source")
    assert response.status_code == 400
    assert "Invalid source" in response.json()["detail"]
