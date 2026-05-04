# Search: Combined "BUSINESS_UNIT_CD-DISPLAY_NAME" Label

**Date:** 2026-05-04
**Status:** Approved — ready for implementation planning

## Problem

Users want the sidebar search to work against a combined store label (e.g., `"B6-Natick"`) regardless of which table is selected (Business Unit Details or Web Names). Today:

- Business Unit Details search matches only `STORE_CD`, so typing `"Natick"` there returns nothing.
- Web Names search matches `DISPLAY_NAME`, `CITY`, `BUSINESS_UNIT_CD` — but the input text stays whatever was typed.
- There is no single canonical identifier shown to the user in the search control.

## Goal

One search input drives both table views. If the user types a term that uniquely identifies a store (either `B6` or `Natick`), the input auto-transforms to `"B6-Natick"` and both tables filter to that store. Ambiguous or missing matches leave the typed text alone.

## Behavior

1. User types into the sidebar search input.
2. App looks up all combined labels from a cached join of `BUSINESS_UNIT_DETAILS` and `BUSINESS_UNIT_WEB_NAME`.
3. App matches the typed term case-insensitively against `BUSINESS_UNIT_CD`, `DISPLAY_NAME`, and the combined label.
4. **Exactly one match** → the input value is replaced with `"B6-Natick"`, both tables filter to that store.
5. **Multiple matches** → input stays as typed; both tables show all matching rows.
6. **Zero matches** → input stays as typed; "No records found" shown.
7. The same search term filters both views consistently, so switching the radio button shows the same store.

## Data source for the lookup

New cached helper `get_store_labels()` runs:

```sql
SELECT
    bd.STORE_CD,
    wn.BUSINESS_UNIT_CD,
    wn.DISPLAY_NAME,
    wn.BUSINESS_UNIT_CD || '-' || wn.DISPLAY_NAME AS COMBINED_LABEL
FROM <business_unit_details> bd
LEFT JOIN <business_unit_web_name> wn
    ON bd.STORE_CD = wn.BUSINESS_UNIT_CD
WHERE wn.BUSINESS_UNIT_CD IS NOT NULL
```

- Cached via `@st.cache_data(ttl=300)` — same TTL as other read queries.
- Respects `config/table_config.py` (backup vs. production).
- Stores without a `BUSINESS_UNIT_WEB_NAME` row are excluded from the lookup; they cannot produce a combined label.

## Implementation touchpoints

**1. `src/database/snowflake_operations.py`**
- Add `get_store_labels()` — returns DataFrame with `BUSINESS_UNIT_CD`, `DISPLAY_NAME`, `COMBINED_LABEL`. Cached 5 min.
- Modify `get_business_units()` to also match on `BUSINESS_UNIT_CD` / `DISPLAY_NAME` via a join, so typing `"Natick"` from the Business Unit Details tab also filters. If the search term contains `-`, extract the prefix (`B6`) and match on `STORE_CD`.
- Modify `get_web_names()` similarly: if search term contains `-`, match on `BUSINESS_UNIT_CD` by the prefix.

**2. `app.py` — `render_sidebar()`**
- Between text-input capture and session-state assignment, call `get_store_labels()`.
- Match typed term against `BUSINESS_UNIT_CD`, `DISPLAY_NAME`, `COMBINED_LABEL` (case-insensitive `contains`).
- If exactly one unique `COMBINED_LABEL` matches → overwrite `st.session_state.search_term` with that label, `st.rerun()` so the input reflects it.
- Otherwise leave `search_term` as typed.

**3. Query call sites** — no change at the call site; behavior shift lives inside the two query functions.

## Edge cases

| Case | Input | Outcome |
|------|-------|---------|
| A | `B6` (unique) | Box → `B6-Natick`; both tables filter to one store |
| B | `Natick` (unique) | Box → `B6-Natick`; both tables filter to one store |
| C | `new` (matches B6-New York, B7-New Haven, B8-Newark) | Box stays `new`; tables show 3 rows |
| D | `XYZ` (no match) | Box stays `XYZ`; "No records found" |
| E | `B6-Natick` (direct) | No transformation; tables filter to that store |
| F | Store with no web-name row | Not in lookup; combined label not produced |
| G | Snowflake fails during `get_store_labels()` | Log error, return empty DataFrame, fall back to raw typed-text filtering |
| H | Clear button | `search_term` reset to `""` (existing behavior) |

## Out of scope

- No new column added to the data tables.
- No changes to the edit forms.
- No changes to `update_business_unit` / `update_web_name`.
- No dropdown/selectbox UI — the text input is preserved.
