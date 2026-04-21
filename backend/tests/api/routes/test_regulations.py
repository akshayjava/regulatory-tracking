import pytest

def test_regulation_updates_logging_history(client, test_db):
    # Setup initial state
    from backend.api.database import get_db
    with get_db() as conn:
        conn.execute("INSERT INTO agencies (id, name, abbreviation) VALUES (1, 'Test Agency', 'TA')")
        conn.execute("""
            INSERT INTO regulations (
                id, regulation_id, title, type, status, source, complexity_score, impact_score
            ) VALUES (
                1, 'reg-1', 'Initial Title', 'rule', 'proposed', 'sec', 5, 5
            )
        """)
        conn.commit()

    # 1. Update the regulation via API
    updates = {
        "title": "Updated Title",
        "status": "final",
        "impact_score": 8
    }

    response = client.put("/regulations/reg-1", json=updates)
    assert response.status_code == 200

    # 2. Query the history table to assert insertions
    with get_db() as conn:
        rows = conn.execute("SELECT field_changed, old_value, new_value FROM regulation_history WHERE regulation_id = 1").fetchall()

    history = {row['field_changed']: {'old': row['old_value'], 'new': row['new_value']} for row in rows}

    assert len(history) == 3
    assert history['title']['old'] == 'Initial Title'
    assert history['title']['new'] == 'Updated Title'
    assert history['status']['old'] == 'proposed'
    assert history['status']['new'] == 'final'
    assert history['impact_score']['old'] == '5'
    assert history['impact_score']['new'] == '8'
