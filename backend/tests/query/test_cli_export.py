import os
import csv
import sqlite3
import tempfile
import pytest
from click.testing import CliRunner

from query.cli import cli

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Initialize schema
    conn = sqlite3.connect(path)
    # schema.sql is at backend/db/schema.sql
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db", "schema.sql")
    with open(schema_path, "r") as f:
        conn.executescript(f.read())

    # Insert dummy data
    conn.execute("INSERT INTO agencies (id, name, abbreviation) VALUES (1, 'Test Agency', 'TA')")

    # Reg 1: Crypto, Effective
    conn.execute("""
        INSERT INTO regulations (id, regulation_id, title, type, status, source, impact_score, agency_id)
        VALUES (1, 'reg-001', 'Crypto Rule', 'rule', 'effective', 'sec', 8, 1)
    """)
    conn.execute("INSERT INTO regulation_verticals (regulation_id, vertical) VALUES (1, 'crypto')")

    # Reg 2: Fintech, Proposed
    conn.execute("""
        INSERT INTO regulations (id, regulation_id, title, type, status, source, impact_score, agency_id)
        VALUES (2, 'reg-002', 'Fintech Rule', 'rule', 'proposed', 'sec', 5, 1)
    """)
    conn.execute("INSERT INTO regulation_verticals (regulation_id, vertical) VALUES (2, 'fintech')")

    # Reg 3: Healthcare, Effective
    conn.execute("""
        INSERT INTO regulations (id, regulation_id, title, type, status, source, impact_score, agency_id)
        VALUES (3, 'reg-003', 'Health Rule', 'rule', 'effective', 'fda', 9, 1)
    """)
    conn.execute("INSERT INTO regulation_verticals (regulation_id, vertical) VALUES (3, 'healthcare')")

    conn.commit()
    conn.close()

    yield path
    os.remove(path)

@pytest.fixture
def setup_cli_env(temp_db, monkeypatch):
    monkeypatch.setenv("DB_PATH", temp_db)
    import query.cli
    monkeypatch.setattr(query.cli, "DB_PATH", temp_db)
    return temp_db

def test_export_all(setup_cli_env):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["export", "--output", "test_out.csv"])
        assert result.exit_code == 0
        assert "Exported 3 regulations to test_out.csv" in result.output

        assert os.path.exists("test_out.csv")
        with open("test_out.csv", "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
            # Should be ordered by impact score DESC: 9, 8, 5
            assert rows[0]["impact_score"] == "9"
            assert rows[1]["impact_score"] == "8"
            assert rows[2]["impact_score"] == "5"
            assert rows[0]["agency"] == "TA"

def test_export_filter_vertical(setup_cli_env):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["export", "--vertical", "crypto", "--output", "crypto.csv"])
        assert result.exit_code == 0
        assert "Exported 1 regulations to crypto.csv" in result.output

        with open("crypto.csv", "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["title"] == "Crypto Rule"

def test_export_filter_status(setup_cli_env):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["export", "--status", "effective", "--output", "eff.csv"])
        assert result.exit_code == 0
        assert "Exported 2 regulations to eff.csv" in result.output

        with open("eff.csv", "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            statuses = [r["status"] for r in rows]
            assert all(s == "effective" for s in statuses)

def test_export_filter_vertical_and_status(setup_cli_env):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["export", "--vertical", "crypto", "--status", "effective", "--output", "comb.csv"])
        assert result.exit_code == 0
        assert "Exported 1 regulations to comb.csv" in result.output
