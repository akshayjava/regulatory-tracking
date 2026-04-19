import os
import sqlite3
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def test_db():
    fd, path = tempfile.mkstemp()

    # We must patch the DB_PATH module variable directly as it's evaluated at import
    with patch('backend.api.database.DB_PATH', path):
        # We also need to patch os.environ in case something else checks it
        with patch.dict(os.environ, {'DB_PATH': path}):
            from backend.api.database import init_db
            init_db()
            yield path

    os.close(fd)
    os.unlink(path)

@pytest.fixture
def client(test_db):
    # This must be imported after DB_PATH is patched
    from backend.api.main import app
    return TestClient(app)
