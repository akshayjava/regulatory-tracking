import pytest

def test_list_regulations_invalid_vertical(client):
    response = client.get("/regulations/", params={"vertical": "invalid_vertical"})
    assert response.status_code == 400
    assert "Invalid vertical" in response.json()["detail"]

def test_list_regulations_invalid_status(client):
    response = client.get("/regulations/", params={"status": "invalid_status"})
    assert response.status_code == 400
    assert "Invalid status" in response.json()["detail"]

def test_list_regulations_valid_vertical_and_status(client):
    response = client.get("/regulations/", params={"vertical": "crypto", "status": "proposed"})
    assert response.status_code == 200
