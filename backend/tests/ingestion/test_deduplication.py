import pytest
from backend.ingestion.deduplication import normalize_regulation_id

def test_normalize_regulation_id_basic():
    """Test basic functionality with typical input."""
    assert normalize_regulation_id("A basic title", "source1", "2023-01-01") == "source1_a_basic_title_2023"

def test_normalize_regulation_id_special_characters():
    """Test that special characters are removed."""
    assert normalize_regulation_id("Title with special characters: !@#$%^&*()_+", "source_a", "2022-05-10") == "source_a_title_with_special_characters_2022"
    assert normalize_regulation_id("Another-title[here]", "source_b", "2024-11-20") == "source_b_anothertitlehere_2024"

def test_normalize_regulation_id_whitespace():
    """Test that multiple spaces are converted to single underscores and leading/trailing whitespace is handled."""
    assert normalize_regulation_id("  Lots   of    spaces  ", "source_x", "2021-02-02") == "source_x_lots_of_spaces_2021"
    assert normalize_regulation_id("\tTabs\nand\rnewlines\n", "source_y", "2020-10-10") == "source_y_tabs_and_newlines_2020"

def test_normalize_regulation_id_truncation():
    """Test that slugs are truncated to 60 characters and trailing underscores are stripped."""
    long_title = "This is a very long title that should definitely be truncated because it exceeds the sixty character limit we set"
    # Expected slug calculation:
    # lower: "this is a very long title that should definitely be truncated because it exceeds the sixty character limit we set"
    # re.sub special: same
    # re.sub spaces: "this_is_a_very_long_title_that_should_definitely_be_truncated_because_it_exceeds_the_sixty_character_limit_we_set"
    # length 60: "this_is_a_very_long_title_that_should_definitely_be_truncate"
    assert normalize_regulation_id(long_title, "source_z", "2025-01-01") == "source_z_this_is_a_very_long_title_that_should_definitely_be_truncate_2025"

    # Truncation landing exactly on an underscore
    title_landing_on_underscore = "a" * 59 + " b"
    # "a"*59 + "_b" -> truncated to 60 is "a"*59 + "_"
    # trailing "_" is rstripped -> "a"*59
    assert normalize_regulation_id(title_landing_on_underscore, "src", "2023-01-01") == f"src_{'a'*59}_2023"

def test_normalize_regulation_id_empty_date():
    """Test that missing or empty dates result in year 0000."""
    assert normalize_regulation_id("No date title", "src1", "") == "src1_no_date_title_0000"
    assert normalize_regulation_id("None date title", "src2", None) == "src2_none_date_title_0000"

def test_normalize_regulation_id_empty_title():
    """Test behavior with an empty title."""
    assert normalize_regulation_id("", "src", "2023-01-01") == "src__2023"

def test_normalize_regulation_id_only_special_characters():
    """Test behavior with title containing only special characters."""
    assert normalize_regulation_id("!@#$%^&*", "src", "2023-01-01") == "src__2023"

def test_normalize_regulation_id_case_insensitivity():
    """Test that titles are consistently lowercased."""
    assert normalize_regulation_id("UPPERCASE TITLE", "src", "2023-01-01") == "src_uppercase_title_2023"
    assert normalize_regulation_id("MiXeD CaSe", "src", "2023-01-01") == "src_mixed_case_2023"

def test_normalize_regulation_id_short_date():
    """Test behavior with dates shorter than 4 characters."""
    assert normalize_regulation_id("Short date", "src", "123") == "src_short_date_123"
