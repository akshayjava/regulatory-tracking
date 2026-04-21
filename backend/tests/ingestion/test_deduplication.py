import pytest
from ingestion.deduplication import _title_similarity

def test_title_similarity_identical():
    assert _title_similarity("Financial Regulation A", "Financial Regulation A") == 1.0

def test_title_similarity_disjoint():
    assert _title_similarity("Financial Regulation A", "Banking Standard B") == 0.0

def test_title_similarity_empty():
    assert _title_similarity("", "") == 0.0
    assert _title_similarity("Title", "") == 0.0
    assert _title_similarity("", "Title") == 0.0

def test_title_similarity_case_insensitivity():
    assert _title_similarity("FINANCIAL REGULATION", "financial regulation") == 1.0

def test_title_similarity_partial_overlap():
    # "Financial Regulation A" (3 words) vs "Financial Regulation B" (3 words)
    # Intersection: "financial", "regulation" (2 words)
    # Result: 2 / max(3, 3) = 2/3 = 0.666...
    assert _title_similarity("Financial Regulation A", "Financial Regulation B") == pytest.approx(2.0/3.0)

    # "New Banking Rules" (3 words) vs "Rules for New Banking" (4 words)
    # Intersection: "new", "banking", "rules" (3 words)
    # Result: 3 / max(3, 4) = 3/4 = 0.75
    assert _title_similarity("New Banking Rules", "Rules for New Banking") == 0.75

def test_title_similarity_duplicate_words():
    # "Financial Financial" -> set("financial") (1 word)
    # "Financial" -> set("financial") (1 word)
    # Result: 1 / max(1, 1) = 1.0
    assert _title_similarity("Financial Financial", "Financial") == 1.0
