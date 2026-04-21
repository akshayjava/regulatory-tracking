import os
import tempfile
import pytest

from fastapi.testclient import TestClient

# Mock DB_PATH before importing app or routes
fd, path = tempfile.mkstemp()
os.environ["DB_PATH"] = path

from backend.api.main import app
from backend.api.database import init_db, get_db

# Make sure to override the module level DB_PATH as well, as it is evaluated at import time
import backend.api.database
backend.api.database.DB_PATH = path

@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    init_db()
    yield
    os.close(fd)
    os.unlink(path)

@pytest.fixture(scope="function")
def db_conn():
    with get_db() as conn:
        yield conn

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c
