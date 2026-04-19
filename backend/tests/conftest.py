import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.api.database import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    import os
    os.environ["DB_PATH"] = ":memory:"
    init_db()

@pytest.fixture
def client():
    return TestClient(app)
