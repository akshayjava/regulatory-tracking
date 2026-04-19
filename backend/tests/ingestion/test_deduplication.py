from ingestion.deduplication import _title_similarity

def test_title_similarity_empty():
    assert _title_similarity("", "") == 0.0
    assert _title_similarity("", "text") == 0.0
    assert _title_similarity("text", "") == 0.0

def test_title_similarity_exact():
    assert _title_similarity("hello world", "hello world") == 1.0

def test_title_similarity_partial():
    assert _title_similarity("hello world", "hello friend") == 0.5
    assert _title_similarity("the quick brown fox", "the quick silver fox") == 0.75

def test_title_similarity_disjoint():
    assert _title_similarity("foo bar", "baz qux") == 0.0

def test_title_similarity_case_insensitivity():
    assert _title_similarity("Hello World", "hello world") == 1.0

def test_title_similarity_extra_spaces():
    assert _title_similarity("hello   world", "hello world") == 1.0
