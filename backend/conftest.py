import os
import tempfile
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def setup_test_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)

    os.environ["DB_PATH"] = path

    # Patch module level variable
    try:
        from api import database
        database.DB_PATH = path
        database.init_db()
    except ImportError:
        pass

    yield path

    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def client():
    # Setup test env var before importing app
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    from api.main import app
    with TestClient(app) as test_client:
        yield test_client
