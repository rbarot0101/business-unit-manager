"""Pure-Python helper for transforming a sidebar search term into a
combined "BUSINESS_UNIT_CD-DISPLAY_NAME" label when it uniquely matches
a known store.
"""

from typing import List, Optional


def resolve_search_term(typed: str, labels: List[dict]) -> Optional[str]:
    """Return the transformed label if `typed` uniquely identifies one store,
    otherwise return the typed term unchanged. Returns an empty string if
    `typed` is empty.

    Each entry in `labels` must have keys: 'BUSINESS_UNIT_CD', 'DISPLAY_NAME',
    'COMBINED_LABEL'.
    """
    raise NotImplementedError
