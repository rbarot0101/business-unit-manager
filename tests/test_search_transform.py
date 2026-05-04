from src.utils.search_transform import resolve_search_term


SAMPLE_LABELS = [
    {"BUSINESS_UNIT_CD": "B6", "DISPLAY_NAME": "Natick", "COMBINED_LABEL": "B6-Natick"},
    {"BUSINESS_UNIT_CD": "B7", "DISPLAY_NAME": "Albany", "COMBINED_LABEL": "B7-Albany"},
    {"BUSINESS_UNIT_CD": "B8", "DISPLAY_NAME": "New York", "COMBINED_LABEL": "B8-New York"},
    {"BUSINESS_UNIT_CD": "B9", "DISPLAY_NAME": "New Haven", "COMBINED_LABEL": "B9-New Haven"},
]


def test_empty_term_returns_empty():
    assert resolve_search_term("", SAMPLE_LABELS) == ""


def test_unique_match_by_business_unit_cd_transforms():
    assert resolve_search_term("B6", SAMPLE_LABELS) == "B6-Natick"


def test_unique_match_is_case_insensitive():
    assert resolve_search_term("b6", SAMPLE_LABELS) == "B6-Natick"


def test_unique_match_by_display_name_transforms():
    assert resolve_search_term("Natick", SAMPLE_LABELS) == "B6-Natick"


def test_exact_combined_label_is_returned_unchanged():
    assert resolve_search_term("B6-Natick", SAMPLE_LABELS) == "B6-Natick"


def test_ambiguous_term_returns_typed_unchanged():
    # "new" matches both "B8-New York" and "B9-New Haven"
    assert resolve_search_term("new", SAMPLE_LABELS) == "new"


def test_no_match_returns_typed_unchanged():
    assert resolve_search_term("XYZ", SAMPLE_LABELS) == "XYZ"
