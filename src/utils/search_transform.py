"""Pure-Python helper for transforming a sidebar search term into a
combined "BUSINESS_UNIT_CD-DISPLAY_NAME" label when it uniquely matches
a known store.
"""

from typing import List


def resolve_search_term(typed: str, labels: List[dict]) -> str:
    """Return the transformed label if `typed` uniquely identifies one store,
    otherwise return the typed term unchanged. Returns an empty string if
    `typed` is empty.

    Each entry in `labels` must have keys: 'BUSINESS_UNIT_CD', 'DISPLAY_NAME',
    'COMBINED_LABEL'.
    """
    if not typed:
        return ""

    needle = typed.casefold()
    matches = [
        row for row in labels
        if needle in row["BUSINESS_UNIT_CD"].casefold()
        or needle in row["DISPLAY_NAME"].casefold()
        or needle in row["COMBINED_LABEL"].casefold()
    ]

    unique_labels = {row["COMBINED_LABEL"] for row in matches}
    if len(unique_labels) == 1:
        return next(iter(unique_labels))

    return typed
