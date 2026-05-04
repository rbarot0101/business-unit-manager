# Combined Store-Label Search Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Auto-transform the sidebar search term to `"BUSINESS_UNIT_CD-DISPLAY_NAME"` on unique match, so typing either `B6` or `Natick` becomes `B6-Natick` and filters both table views consistently.

**Architecture:** A new cached helper `get_store_labels()` queries a join of `BUSINESS_UNIT_DETAILS` and `BUSINESS_UNIT_WEB_NAME` to build a lookup of all combined labels. A pure-Python helper `resolve_search_term()` takes the typed term plus the lookup and returns either the transformed label (unique match) or the original term (ambiguous / no match). The existing Streamlit sidebar calls the helper, updates `st.session_state.search_term`, and the existing query functions are widened to understand a `"PREFIX-SUFFIX"` search term and to search across more fields.

**Tech Stack:** Streamlit, Snowflake connector, pandas, pytest (added for this feature).

**Design doc:** `docs/plans/2026-05-04-search-combined-label-design.md`

---

## Task 1: Set up pytest and a home for the new pure-Python helper

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_search_transform.py`
- Create: `src/utils/search_transform.py`
- Modify: `requirements.txt`

**Step 1: Add pytest to requirements**

Open `requirements.txt` and append on a new line:

```
pytest>=7.0
```

**Step 2: Install pytest**

Run: `pip install pytest`
Expected: `Successfully installed pytest-...`

**Step 3: Create the empty test package and module**

Create `tests/__init__.py` with empty contents.

Create `src/utils/search_transform.py` with a stub:

```python
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
```

**Step 4: Commit scaffolding**

```bash
git add requirements.txt tests/__init__.py src/utils/search_transform.py
git commit -m "Scaffold search_transform module and pytest setup"
```

---

## Task 2: Test — empty typed term returns empty string

**Files:**
- Modify: `tests/test_search_transform.py`

**Step 1: Write the failing test**

```python
from src.utils.search_transform import resolve_search_term


SAMPLE_LABELS = [
    {"BUSINESS_UNIT_CD": "B6", "DISPLAY_NAME": "Natick", "COMBINED_LABEL": "B6-Natick"},
    {"BUSINESS_UNIT_CD": "B7", "DISPLAY_NAME": "Albany", "COMBINED_LABEL": "B7-Albany"},
    {"BUSINESS_UNIT_CD": "B8", "DISPLAY_NAME": "New York", "COMBINED_LABEL": "B8-New York"},
    {"BUSINESS_UNIT_CD": "B9", "DISPLAY_NAME": "New Haven", "COMBINED_LABEL": "B9-New Haven"},
]


def test_empty_term_returns_empty():
    assert resolve_search_term("", SAMPLE_LABELS) == ""
```

**Step 2: Run it — expect failure**

Run: `pytest tests/test_search_transform.py::test_empty_term_returns_empty -v`
Expected: FAIL with `NotImplementedError`.

**Step 3: Implement minimum to pass**

In `src/utils/search_transform.py`, replace the stub body:

```python
def resolve_search_term(typed: str, labels: List[dict]) -> Optional[str]:
    if not typed:
        return ""
    raise NotImplementedError
```

**Step 4: Run — expect pass**

Run: `pytest tests/test_search_transform.py::test_empty_term_returns_empty -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add tests/test_search_transform.py src/utils/search_transform.py
git commit -m "Handle empty search term in resolve_search_term"
```

---

## Task 3: Test — unique match by BUSINESS_UNIT_CD transforms to combined label

**Files:**
- Modify: `tests/test_search_transform.py`

**Step 1: Write the failing test**

Append to `tests/test_search_transform.py`:

```python
def test_unique_match_by_business_unit_cd_transforms():
    assert resolve_search_term("B6", SAMPLE_LABELS) == "B6-Natick"


def test_unique_match_is_case_insensitive():
    assert resolve_search_term("b6", SAMPLE_LABELS) == "B6-Natick"
```

**Step 2: Run — expect failure**

Run: `pytest tests/test_search_transform.py -v`
Expected: the two new tests FAIL with `NotImplementedError`; previous test still passes.

**Step 3: Implement the matching logic**

Replace the body of `resolve_search_term` with:

```python
def resolve_search_term(typed: str, labels: List[dict]) -> Optional[str]:
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
```

**Step 4: Run — expect pass**

Run: `pytest tests/test_search_transform.py -v`
Expected: all three tests PASS.

**Step 5: Commit**

```bash
git add tests/test_search_transform.py src/utils/search_transform.py
git commit -m "Resolve unique match by business unit code"
```

---

## Task 4: Test — unique match by DISPLAY_NAME and by full combined label

**Files:**
- Modify: `tests/test_search_transform.py`

**Step 1: Write the failing tests**

Append:

```python
def test_unique_match_by_display_name_transforms():
    assert resolve_search_term("Natick", SAMPLE_LABELS) == "B6-Natick"


def test_exact_combined_label_is_returned_unchanged():
    assert resolve_search_term("B6-Natick", SAMPLE_LABELS) == "B6-Natick"
```

**Step 2: Run — expect pass**

Run: `pytest tests/test_search_transform.py -v`
Expected: all tests PASS (the implementation from Task 3 already covers these cases).

Note: if either of these fails, stop and diagnose — something is off in Task 3's implementation.

**Step 3: Commit**

```bash
git add tests/test_search_transform.py
git commit -m "Cover display-name and full-label search cases"
```

---

## Task 5: Test — ambiguous term returns typed text unchanged

**Files:**
- Modify: `tests/test_search_transform.py`

**Step 1: Write the failing test**

Append:

```python
def test_ambiguous_term_returns_typed_unchanged():
    # "new" matches both "B8-New York" and "B9-New Haven"
    assert resolve_search_term("new", SAMPLE_LABELS) == "new"


def test_no_match_returns_typed_unchanged():
    assert resolve_search_term("XYZ", SAMPLE_LABELS) == "XYZ"
```

**Step 2: Run — expect pass**

Run: `pytest tests/test_search_transform.py -v`
Expected: all tests PASS (Task 3's logic already handles these).

**Step 3: Commit**

```bash
git add tests/test_search_transform.py
git commit -m "Cover ambiguous and no-match search cases"
```

---

## Task 6: Add `get_store_labels()` to snowflake_operations

**Files:**
- Modify: `src/database/snowflake_operations.py`

**Step 1: Add the function**

Open `src/database/snowflake_operations.py`. After the existing `get_web_names()` function (around line 113), add:

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_store_labels() -> pd.DataFrame:
    """
    Fetch the join of business unit details and web names, producing one row
    per store with columns BUSINESS_UNIT_CD, DISPLAY_NAME, and COMBINED_LABEL
    ("BUSINESS_UNIT_CD-DISPLAY_NAME"). Used to resolve sidebar search terms
    into a canonical store label.

    Returns:
        DataFrame with columns: BUSINESS_UNIT_CD, DISPLAY_NAME, COMBINED_LABEL
    """
    try:
        conn = get_snowflake_connection()
        tables = get_table_names()
        bu_table = f"ODS.PUBLIC.{tables['business_unit_details']}"
        wn_table = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

        query = f"""
            SELECT
                wn.BUSINESS_UNIT_CD,
                wn.DISPLAY_NAME,
                wn.BUSINESS_UNIT_CD || '-' || wn.DISPLAY_NAME AS COMBINED_LABEL
            FROM {bu_table} bd
            JOIN {wn_table} wn
                ON bd.STORE_CD = wn.BUSINESS_UNIT_CD
            WHERE wn.BUSINESS_UNIT_CD IS NOT NULL
              AND wn.DISPLAY_NAME IS NOT NULL
        """

        logger.debug(f"Executing query: {query}")
        cursor = conn.cursor()
        cursor.execute(query)
        df = cursor.fetch_pandas_all()
        logger.info(f"Fetched {len(df)} store labels")
        return df

    except Exception as e:
        logger.error(f"Error fetching store labels: {e}")
        return pd.DataFrame(columns=["BUSINESS_UNIT_CD", "DISPLAY_NAME", "COMBINED_LABEL"])
```

**Step 2: Quick smoke verification**

Run:

```bash
python -c "from src.database.snowflake_operations import get_store_labels; df = get_store_labels(); print(df.head()); print('rows:', len(df))"
```

Expected: prints a small DataFrame with `BUSINESS_UNIT_CD`, `DISPLAY_NAME`, `COMBINED_LABEL` columns and a row count > 0.

If the command errors on Streamlit cache outside a Streamlit session, that's fine — skip the smoke check and rely on the Streamlit end-to-end verification in Task 10.

**Step 3: Commit**

```bash
git add src/database/snowflake_operations.py
git commit -m "Add get_store_labels helper for search resolution"
```

---

## Task 7: Widen `get_business_units()` to accept combined labels and join on web name

**Files:**
- Modify: `src/database/snowflake_operations.py` (the `get_business_units` function, lines ~30–63)

**Step 1: Replace the function body**

Replace the entire `get_business_units` function with:

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_business_units(search_term: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch business unit details. The search term may be a raw STORE_CD,
    a DISPLAY_NAME fragment, or a combined "STORE_CD-DISPLAY_NAME" label.
    When a combined label is provided (contains '-'), only the prefix is used
    to filter on STORE_CD.
    """
    try:
        conn = get_snowflake_connection()
        tables = get_table_names()
        bu_table = f"ODS.PUBLIC.{tables['business_unit_details']}"
        wn_table = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

        base_query = f"SELECT bd.* FROM {bu_table} bd"

        params: Dict[str, Any] = {}
        where_clause = ""

        if search_term:
            if "-" in search_term:
                prefix = search_term.split("-", 1)[0]
                where_clause = " WHERE bd.STORE_CD ILIKE :needle"
                params["needle"] = f"%{prefix}%"
            else:
                # Search STORE_CD directly and DISPLAY_NAME via the web-name join
                base_query += (
                    f" LEFT JOIN {wn_table} wn ON bd.STORE_CD = wn.BUSINESS_UNIT_CD"
                )
                where_clause = (
                    " WHERE bd.STORE_CD ILIKE :needle"
                    " OR wn.DISPLAY_NAME ILIKE :needle"
                    " OR wn.BUSINESS_UNIT_CD ILIKE :needle"
                )
                params["needle"] = f"%{search_term}%"

        query = base_query + where_clause + " ORDER BY bd.STORE_CD"

        logger.debug(f"Executing query: {query} params={params}")
        cursor = conn.cursor()
        cursor.execute(query, params)
        df = cursor.fetch_pandas_all()
        logger.info(f"Fetched {len(df)} business unit records from {bu_table}")
        return df

    except Exception as e:
        logger.error(f"Error fetching business units: {e}")
        st.error(f"Failed to fetch business units: {str(e)}")
        return pd.DataFrame()
```

Security note: this uses bind parameters for the search term. Do not reintroduce f-string interpolation of user input.

**Step 2: Commit**

```bash
git add src/database/snowflake_operations.py
git commit -m "Widen business units search to DISPLAY_NAME and combined labels"
```

---

## Task 8: Widen `get_web_names()` to understand combined labels

**Files:**
- Modify: `src/database/snowflake_operations.py` (the `get_web_names` function, lines ~66–113)

**Step 1: Replace the function body**

Replace the entire `get_web_names` function with:

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_web_names(search_term: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch web-name records joined with business unit details. The search term
    may be a raw code/name or a combined "BUSINESS_UNIT_CD-DISPLAY_NAME" label.
    When a combined label is provided, only the prefix is used to match on
    BUSINESS_UNIT_CD.
    """
    try:
        conn = get_snowflake_connection()
        tables = get_table_names()
        bu_table = f"ODS.PUBLIC.{tables['business_unit_details']}"
        wn_table = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

        base_query = f"""
            SELECT
                bd.STORE_CD,
                wn.BUSINESS_UNIT_CD,
                wn.DISPLAY_NAME,
                wn.ADDRESS_LINE_1,
                wn.ADDRESS_LINE_2,
                wn.CITY,
                wn.STATE,
                wn.POSTAL_CODE
            FROM {bu_table} bd
            LEFT JOIN {wn_table} wn
                ON bd.STORE_CD = wn.BUSINESS_UNIT_CD
        """

        params: Dict[str, Any] = {}
        where_clause = ""

        if search_term:
            if "-" in search_term:
                prefix = search_term.split("-", 1)[0]
                where_clause = " WHERE wn.BUSINESS_UNIT_CD ILIKE :needle"
                params["needle"] = f"%{prefix}%"
            else:
                where_clause = (
                    " WHERE wn.DISPLAY_NAME ILIKE :needle"
                    " OR wn.CITY ILIKE :needle"
                    " OR wn.BUSINESS_UNIT_CD ILIKE :needle"
                )
                params["needle"] = f"%{search_term}%"

        query = base_query + where_clause + " ORDER BY bd.STORE_CD"

        logger.debug(f"Executing query: {query} params={params}")
        cursor = conn.cursor()
        cursor.execute(query, params)
        df = cursor.fetch_pandas_all()
        logger.info(f"Fetched {len(df)} web name records from {wn_table}")
        return df

    except Exception as e:
        logger.error(f"Error fetching web names: {e}")
        st.error(f"Failed to fetch web names: {str(e)}")
        return pd.DataFrame()
```

**Step 2: Commit**

```bash
git add src/database/snowflake_operations.py
git commit -m "Parameterize and extend web names search"
```

---

## Task 9: Wire the search-transform into the sidebar

**Files:**
- Modify: `app.py` (imports block and `render_sidebar()`, lines ~11–28 and ~132–218)

**Step 1: Add imports**

In the imports block near the top of `app.py`, add:

```python
from src.database.snowflake_operations import (
    get_snowflake_connection,
    get_business_units,
    get_web_names,
    get_store_labels,
    update_business_unit,
    update_web_name,
)
from src.utils.search_transform import resolve_search_term
```

(Merge these with the existing import statements — do not duplicate.)

**Step 2: Transform the search term inside `render_sidebar`**

Find the block currently reading:

```python
    search_input = st.sidebar.text_input(
        "Search records",
        value=st.session_state.search_term,
        placeholder="Enter search term...",
        key="search_input"
    )
    st.session_state.search_term = search_input
```

Replace it with:

```python
    search_input = st.sidebar.text_input(
        "Search records",
        value=st.session_state.search_term,
        placeholder="Enter search term...",
        key="search_input"
    )

    if search_input != st.session_state.search_term:
        labels_df = get_store_labels()
        labels = labels_df.to_dict("records") if not labels_df.empty else []
        resolved = resolve_search_term(search_input, labels)
        st.session_state.search_term = resolved
        if resolved != search_input:
            st.rerun()
```

The guard `search_input != st.session_state.search_term` avoids recomputing on every rerun when nothing changed. The `st.rerun()` call fires only when the typed text was actually transformed, so the text input re-renders with the combined label.

**Step 3: Commit**

```bash
git add app.py
git commit -m "Transform sidebar search term to combined store label"
```

---

## Task 10: Manual end-to-end verification

**Files:** none — this task is runtime verification.

**Step 1: Launch the app**

Run: `streamlit run app.py`

**Step 2: Walk the cases**

With the app open in the browser, verify each case. Use the same search box for both radio selections.

| # | Steps | Expected |
|---|-------|----------|
| 1 | Select "Business Unit Details". Type `B6`. | Box updates to `B6-Natick` (or equivalent combined label for your real data). Table filters to that one row. |
| 2 | Clear. Type `Natick`. | Box updates to `B6-Natick`. Table filters to that one row. |
| 3 | Switch radio to "Web Names" without clearing. | Same `B6-Natick` filter applies; table shows the matching web-name row. |
| 4 | Clear. Type a substring that matches multiple stores (e.g., `new`). | Box stays as typed. Both tables show multiple rows. |
| 5 | Clear. Type `XYZ`. | Box stays `XYZ`. Both tables show "No records found." |
| 6 | Clear. Type `B6-Natick` directly. | No flicker or re-transform. Filter applies correctly. |
| 7 | Press the Clear button. | Search box empties; tables show full data. |

**Step 3: If all pass, commit a verification note to the plan**

```bash
git commit --allow-empty -m "Verify combined-label search end-to-end in backup mode"
```

If a case fails, stop — do not proceed. Diagnose the specific failing case; the most likely culprits are:
- Streamlit rerun loop — check the `if resolved != search_input` guard in Task 9.
- SQL bind-parameter error in Task 7/8 — check logs for the `Executing query` line.
- `get_store_labels()` returning empty — check that the join condition `bd.STORE_CD = wn.BUSINESS_UNIT_CD` holds for your data.

---

## Out of scope

- No dropdown/selectbox UI.
- No changes to the edit forms or update functions.
- No new columns in the displayed tables.
- Tests for the SQL functions (they require a live Snowflake connection; covered by manual verification in Task 10).
