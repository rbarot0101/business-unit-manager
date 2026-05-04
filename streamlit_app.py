"""Business Unit Manager - Streamlit in Snowflake Version

Streamlit application for managing business unit information in Snowflake.
This version is optimized to run within Snowflake's Streamlit environment.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from snowflake.snowpark.context import get_active_session

# Page configuration
st.set_page_config(
    page_title="Business Unit Manager",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration - set to True for backup tables, False for production
USE_BACKUP_TABLES = True
BACKUP_DATE = "20260417"

def get_table_names():
    """Get table names based on environment setting."""
    if USE_BACKUP_TABLES:
        return {
            'business_unit_details': f'ZZZ_BUSINESS_UNIT_DETAILS_{BACKUP_DATE}',
            'business_unit_web_name': f'ZZZ_BUSINESS_UNIT_WEB_NAME_{BACKUP_DATE}'
        }
    else:
        return {
            'business_unit_details': 'BUSINESS_UNIT_DETAILS',
            'business_unit_web_name': 'BUSINESS_UNIT_WEB_NAME'
        }

def get_environment_mode():
    """Get current environment mode."""
    return 'BACKUP' if USE_BACKUP_TABLES else 'PRODUCTION'

def is_backup_mode():
    """Check if in backup mode."""
    return USE_BACKUP_TABLES

@st.cache_data(ttl=300)
def get_business_units(search_term=None):
    """Fetch business unit details."""
    session = get_active_session()
    tables = get_table_names()
    bu_table = f"ODS.PUBLIC.{tables['business_unit_details']}"
    wn_table = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

    if search_term and "-" in search_term:
        prefix = search_term.split("-", 1)[0].replace("'", "''")
        query = (
            f"SELECT bd.* FROM {bu_table} bd"
            f" WHERE bd.STORE_CD ILIKE '%{prefix}%'"
            " ORDER BY bd.STORE_CD"
        )
    elif search_term:
        needle = search_term.replace("'", "''")
        query = (
            f"SELECT bd.* FROM {bu_table} bd"
            f" LEFT JOIN {wn_table} wn ON bd.STORE_CD = wn.BUSINESS_UNIT_CD"
            f" WHERE bd.STORE_CD ILIKE '%{needle}%'"
            f" OR wn.DISPLAY_NAME ILIKE '%{needle}%'"
            f" OR wn.BUSINESS_UNIT_CD ILIKE '%{needle}%'"
            " ORDER BY bd.STORE_CD"
        )
    else:
        query = f"SELECT * FROM {bu_table} ORDER BY STORE_CD"

    return session.sql(query).to_pandas()

@st.cache_data(ttl=300)
def get_web_names(search_term=None):
    """Fetch web name details with JOIN."""
    session = get_active_session()
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

    if search_term and "-" in search_term:
        prefix = search_term.split("-", 1)[0].replace("'", "''")
        query = base_query + f" WHERE wn.BUSINESS_UNIT_CD ILIKE '%{prefix}%'"
    elif search_term:
        needle = search_term.replace("'", "''")
        query = base_query + (
            f" WHERE wn.DISPLAY_NAME ILIKE '%{needle}%'"
            f" OR wn.CITY ILIKE '%{needle}%'"
            f" OR wn.BUSINESS_UNIT_CD ILIKE '%{needle}%'"
        )
    else:
        query = base_query
    query += " ORDER BY bd.STORE_CD"

    return session.sql(query).to_pandas()

@st.cache_data(ttl=300)
def get_store_labels():
    """Fetch BUSINESS_UNIT_CD / DISPLAY_NAME / COMBINED_LABEL for search resolution."""
    session = get_active_session()
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
        ORDER BY wn.BUSINESS_UNIT_CD
    """
    return session.sql(query).to_pandas()

def resolve_search_term(typed, labels):
    """Return COMBINED_LABEL if typed uniquely matches one store, else typed."""
    if not typed:
        return ""

    needle = typed.casefold()
    matches = [
        row for row in labels
        if needle in str(row.get("BUSINESS_UNIT_CD", "")).casefold()
        or needle in str(row.get("DISPLAY_NAME", "")).casefold()
        or needle in str(row.get("COMBINED_LABEL", "")).casefold()
    ]

    unique_labels = {row["COMBINED_LABEL"] for row in matches}
    if len(unique_labels) == 1:
        return next(iter(unique_labels))

    return typed

def update_business_unit(store_cd, updates):
    """Update business unit record."""
    try:
        session = get_active_session()
        tables = get_table_names()
        table_name = f"ODS.PUBLIC.{tables['business_unit_details']}"

        # Build SET clause with proper data type handling
        set_parts = []
        for col, val in updates.items():
            if val is None or val == '':
                set_parts.append(f"{col} = NULL")
            elif isinstance(val, bool):
                set_parts.append(f"{col} = {str(val).upper()}")
            elif isinstance(val, (int, float)):
                set_parts.append(f"{col} = {val}")
            elif hasattr(val, 'strftime'):  # Date/datetime object
                set_parts.append(f"{col} = '{val.strftime('%Y-%m-%d')}'")
            elif isinstance(val, str):
                # Escape single quotes in strings
                escaped_val = val.replace("'", "''")
                set_parts.append(f"{col} = '{escaped_val}'")

        set_clause = ", ".join(set_parts)
        query = f"UPDATE {table_name} SET {set_clause} WHERE STORE_CD = '{store_cd}'"

        # Execute the query
        result = session.sql(query).collect()

        # Clear caches
        get_business_units.clear()
        get_web_names.clear()

        st.success(f"Updated record for Store Code: {store_cd}")
        return True
    except Exception as e:
        st.error(f"Update failed: {str(e)}")
        st.error(f"Query attempted: {query if 'query' in locals() else 'N/A'}")
        return False

def update_web_name(business_unit_cd, updates):
    """Update web name record."""
    try:
        session = get_active_session()
        tables = get_table_names()
        table_name = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

        # Build SET clause with proper data type handling
        set_parts = []
        for col, val in updates.items():
            if val is None or val == '':
                set_parts.append(f"{col} = NULL")
            elif isinstance(val, str):
                # Escape single quotes in strings
                escaped_val = val.replace("'", "''")
                set_parts.append(f"{col} = '{escaped_val}'")
            else:
                set_parts.append(f"{col} = '{val}'")

        set_clause = ", ".join(set_parts)
        query = f"UPDATE {table_name} SET {set_clause} WHERE BUSINESS_UNIT_CD = '{business_unit_cd}'"

        # Execute the query
        result = session.sql(query).collect()

        # Clear caches
        get_business_units.clear()
        get_web_names.clear()

        st.success(f"Updated web name for Business Unit: {business_unit_cd}")
        return True
    except Exception as e:
        st.error(f"Update failed: {str(e)}")
        st.error(f"Query attempted: {query if 'query' in locals() else 'N/A'}")
        return False

def initialize_session_state():
    """Initialize session state."""
    if 'selected_table' not in st.session_state:
        st.session_state.selected_table = 'business_units'
    if 'selected_row_index' not in st.session_state:
        st.session_state.selected_row_index = None
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'search_term' not in st.session_state:
        st.session_state.search_term = ""
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    if 'selected_row_data' not in st.session_state:
        st.session_state.selected_row_data = None
    if 'bu_selected_option' not in st.session_state:
        st.session_state.bu_selected_option = "-- Select a record --"
    if 'wn_selected_option' not in st.session_state:
        st.session_state.wn_selected_option = "-- Select a record --"

def render_header():
    """Render header."""
    col1, col2 = st.columns([4, 1])

    with col1:
        st.title("🏢 Business Unit Manager")
        st.caption("Lead: Ram Barot - Lead Data Engineer | Enterprise & Data Analytics Team")

    with col2:
        env_mode = get_environment_mode()
        if is_backup_mode():
            st.success(f"🔒 **{env_mode} MODE**")
        else:
            st.error(f"⚠️ **{env_mode} MODE**")

    st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")

def render_sidebar():
    """Render sidebar."""
    st.sidebar.header("Navigation")

    table_option = st.sidebar.radio(
        "Select Table",
        options=["Business Unit Details", "Web Names"],
        key="table_radio"
    )

    new_table = 'business_units' if table_option == "Business Unit Details" else 'web_names'

    # Clear selection when switching tables
    if 'selected_table' in st.session_state and st.session_state.selected_table != new_table:
        st.session_state.selected_row_data = None
        st.session_state.edit_mode = False
        st.session_state.bu_selected_option = "-- Select a record --"
        st.session_state.wn_selected_option = "-- Select a record --"

    st.session_state.selected_table = new_table

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Search")

    if "search_input" not in st.session_state:
        st.session_state["search_input"] = st.session_state.get("search_term", "")

    def _on_search_change():
        typed = st.session_state.get("search_input", "") or ""
        labels_df = get_store_labels()
        labels = labels_df.to_dict("records") if not labels_df.empty else []
        resolved = resolve_search_term(typed, labels)
        st.session_state.search_term = resolved
        if resolved != typed:
            st.session_state["search_input"] = resolved

    st.sidebar.text_input(
        "Search records",
        placeholder="Enter search term...",
        key="search_input",
        on_change=_on_search_change,
    )

    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            get_business_units.clear()
            get_web_names.clear()
            get_store_labels.clear()
            st.session_state.last_refresh = datetime.now()
            st.experimental_rerun()

    def _on_clear_click():
        st.session_state.selected_row_index = None
        st.session_state.selected_row_data = None
        st.session_state.edit_mode = False
        st.session_state.search_term = ""
        st.session_state["search_input"] = ""
        st.session_state.bu_selected_option = "-- Select a record --"
        st.session_state.wn_selected_option = "-- Select a record --"
        get_business_units.clear()
        get_web_names.clear()

    with col2:
        st.button("✖ Clear", use_container_width=True, on_click=_on_clear_click)

def render_business_units_table():
    """Render business units table."""
    df = get_business_units(st.session_state.search_term)

    if df.empty:
        st.warning("No records found.")
        return

    st.info(f"Showing {len(df)} records")

    # Display dataframe (compatible with older Streamlit versions)
    st.dataframe(df, use_container_width=True, height=400)

    # Row selection using selectbox
    st.markdown("---")
    st.markdown("**📝 Select a record to edit:**")
    st.caption("👇 Use the dropdown below to select a record")

    # Create display options for selectbox
    if not df.empty:
        # Build STORE_CD -> COMBINED_LABEL lookup so dropdown matches the sidebar search format
        labels_df = get_store_labels()
        label_map = {
            row["BUSINESS_UNIT_CD"]: row["COMBINED_LABEL"]
            for _, row in labels_df.iterrows()
        } if not labels_df.empty else {}

        def _bu_label(store_cd):
            return label_map.get(store_cd, store_cd)

        # Create a readable display for each row (matches "BUSINESS_UNIT_CD-DISPLAY_NAME")
        options = ["-- Select a record --"] + [
            _bu_label(row["STORE_CD"]) for _, row in df.iterrows()
        ]

        # Auto-select if only 1 record OR determine index from session state
        current_index = 0
        if len(df) == 1:
            # Auto-select the only available record
            current_index = 1
            auto_selected_option = options[1]
            if st.session_state.bu_selected_option != auto_selected_option:
                st.session_state.bu_selected_option = auto_selected_option
                st.session_state.selected_row_data = df.iloc[0].to_dict()
                st.session_state.edit_mode = True
        elif st.session_state.bu_selected_option != "-- Select a record --":
            # Try to find the stored selection in current options
            for idx, opt in enumerate(options):
                if opt == st.session_state.bu_selected_option:
                    current_index = idx
                    break
            # If stored option not found in current filtered results, reset
            if current_index == 0 and st.session_state.bu_selected_option != "-- Select a record --":
                st.session_state.bu_selected_option = "-- Select a record --"
                st.session_state.selected_row_data = None
                st.session_state.edit_mode = False

        selected_option = st.selectbox(
            "Choose a record:",
            options=options,
            index=current_index,
            key="bu_selectbox"
        )

        if selected_option != "-- Select a record --":
            # Extract store code from the selected option ("STORE_CD-DISPLAY_NAME")
            store_cd = selected_option.split("-", 1)[0]
            # Find the row in dataframe
            selected_row = df[df['STORE_CD'] == store_cd]
            if not selected_row.empty:
                st.session_state.selected_row_data = selected_row.iloc[0].to_dict()
                st.session_state.edit_mode = True
                st.session_state.bu_selected_option = selected_option
                st.success(f"Selected: {selected_option}")
        else:
            # Clear selection if "-- Select a record --" is chosen
            st.session_state.selected_row_data = None
            st.session_state.edit_mode = False
            st.session_state.bu_selected_option = "-- Select a record --"

    if st.session_state.edit_mode and st.session_state.selected_row_data:
        render_business_unit_form()

def render_web_names_table():
    """Render web names table."""
    df = get_web_names(st.session_state.search_term)

    if df.empty:
        st.warning("No records found.")
        return

    st.info(f"Showing {len(df)} records")

    # Display dataframe (compatible with older Streamlit versions)
    st.dataframe(df, use_container_width=True, height=400)

    # Row selection using selectbox
    st.markdown("---")
    st.markdown("**📝 Select a record to edit:**")
    st.caption("👇 Use the dropdown below to select a record")

    # Create display options for selectbox
    if not df.empty:
        # Create a readable display for each row (matches sidebar search "BUSINESS_UNIT_CD-DISPLAY_NAME")
        options = ["-- Select a record --"] + [
            f"{row.get('BUSINESS_UNIT_CD', 'N/A')}-{row.get('DISPLAY_NAME', 'N/A')}"
            for _, row in df.iterrows()
        ]

        # Auto-select if only 1 record OR determine index from session state
        current_index = 0
        if len(df) == 1:
            # Auto-select the only available record
            current_index = 1
            auto_selected_option = options[1]
            if st.session_state.wn_selected_option != auto_selected_option:
                st.session_state.wn_selected_option = auto_selected_option
                st.session_state.selected_row_data = df.iloc[0].to_dict()
                st.session_state.edit_mode = True
        elif st.session_state.wn_selected_option != "-- Select a record --":
            # Try to find the stored selection in current options
            for idx, opt in enumerate(options):
                if opt == st.session_state.wn_selected_option:
                    current_index = idx
                    break
            # If stored option not found in current filtered results, reset
            if current_index == 0 and st.session_state.wn_selected_option != "-- Select a record --":
                st.session_state.wn_selected_option = "-- Select a record --"
                st.session_state.selected_row_data = None
                st.session_state.edit_mode = False

        selected_option = st.selectbox(
            "Choose a record:",
            options=options,
            index=current_index,
            key="wn_selectbox"
        )

        if selected_option != "-- Select a record --":
            # Extract business unit code from the selected option ("BUSINESS_UNIT_CD-DISPLAY_NAME")
            business_unit_cd = selected_option.split("-", 1)[0]
            # Find the row in dataframe
            selected_row = df[df['BUSINESS_UNIT_CD'] == business_unit_cd]
            if not selected_row.empty:
                st.session_state.selected_row_data = selected_row.iloc[0].to_dict()
                st.session_state.edit_mode = True
                st.session_state.wn_selected_option = selected_option
                st.success(f"Selected: {selected_row.iloc[0].get('DISPLAY_NAME')}")
        else:
            # Clear selection if "-- Select a record --" is chosen
            st.session_state.selected_row_data = None
            st.session_state.edit_mode = False
            st.session_state.wn_selected_option = "-- Select a record --"

    if st.session_state.edit_mode and st.session_state.selected_row_data:
        render_web_name_form()

def render_business_unit_form():
    """Render edit form for business units."""
    row = st.session_state.selected_row_data

    with st.expander("✏️ Edit Business Unit", expanded=True):
        with st.form("bu_form"):
            st.subheader(f"Store: {row.get('STORE_CD')}")

            # Coordinates
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Latitude", value=float(row.get('ADDR_LATITUDE', 0)), format="%.6f")
            with col2:
                lon = st.number_input("Longitude", value=float(row.get('ADDR_LONGITUDE', 0)), format="%.6f")

            # Dates
            col1, col2 = st.columns(2)
            with col1:
                open_date = st.date_input("Open Date", value=row.get('OPEN_DATE'))
            with col2:
                close_date = st.date_input("Close Date", value=row.get('CLOSE_DATE'))

            # Store Hours
            st.markdown("**Store Hours**")

            col1, col2 = st.columns(2)
            with col1:
                sun_open = st.text_input("Sunday Open", value=row.get('SUNDAY_OPEN', ''))
            with col2:
                sun_close = st.text_input("Sunday Close", value=row.get('SUNDAY_CLOSE', ''))

            col1, col2 = st.columns(2)
            with col1:
                mon_open = st.text_input("Monday Open", value=row.get('MONDAY_OPEN', ''))
            with col2:
                mon_close = st.text_input("Monday Close", value=row.get('MONDAY_CLOSE', ''))

            col1, col2 = st.columns(2)
            with col1:
                tue_open = st.text_input("Tuesday Open", value=row.get('TUESDAY_OPEN', ''))
            with col2:
                tue_close = st.text_input("Tuesday Close", value=row.get('TUESDAY_CLOSE', ''))

            col1, col2 = st.columns(2)
            with col1:
                wed_open = st.text_input("Wednesday Open", value=row.get('WEDNESDAY_OPEN', ''))
            with col2:
                wed_close = st.text_input("Wednesday Close", value=row.get('WEDNESDAY_CLOSE', ''))

            col1, col2 = st.columns(2)
            with col1:
                thu_open = st.text_input("Thursday Open", value=row.get('THURSDAY_OPEN', ''))
            with col2:
                thu_close = st.text_input("Thursday Close", value=row.get('THURSDAY_CLOSE', ''))

            col1, col2 = st.columns(2)
            with col1:
                fri_open = st.text_input("Friday Open", value=row.get('FRIDAY_OPEN', ''))
            with col2:
                fri_close = st.text_input("Friday Close", value=row.get('FRIDAY_CLOSE', ''))

            col1, col2 = st.columns(2)
            with col1:
                sat_open = st.text_input("Saturday Open", value=row.get('SATURDAY_OPEN', ''))
            with col2:
                sat_close = st.text_input("Saturday Close", value=row.get('SATURDAY_CLOSE', ''))

            # Marketing flag
            marketing = st.checkbox("Marketing Updatable", value=bool(row.get('MARKETING_UPDATABLE')))

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Update", type="primary")
            with col2:
                cancelled = st.form_submit_button("❌ Cancel")

            if submitted:
                if lat < -90 or lat > 90:
                    st.error("Latitude must be between -90 and 90")
                elif lon < -180 or lon > 180:
                    st.error("Longitude must be between -180 and 180")
                else:
                    updates = {
                        'ADDR_LATITUDE': lat,
                        'ADDR_LONGITUDE': lon,
                        'OPEN_DATE': open_date,
                        'CLOSE_DATE': close_date,
                        'SUNDAY_OPEN': sun_open,
                        'SUNDAY_CLOSE': sun_close,
                        'MONDAY_OPEN': mon_open,
                        'MONDAY_CLOSE': mon_close,
                        'TUESDAY_OPEN': tue_open,
                        'TUESDAY_CLOSE': tue_close,
                        'WEDNESDAY_OPEN': wed_open,
                        'WEDNESDAY_CLOSE': wed_close,
                        'THURSDAY_OPEN': thu_open,
                        'THURSDAY_CLOSE': thu_close,
                        'FRIDAY_OPEN': fri_open,
                        'FRIDAY_CLOSE': fri_close,
                        'SATURDAY_OPEN': sat_open,
                        'SATURDAY_CLOSE': sat_close,
                        'MARKETING_UPDATABLE': marketing
                    }
                    if update_business_unit(row.get('STORE_CD'), updates):
                        st.success("Updated successfully!")
                        st.session_state.edit_mode = False
                        st.experimental_rerun()

            if cancelled:
                st.session_state.edit_mode = False
                st.session_state.selected_row_data = None
                st.experimental_rerun()

def render_web_name_form():
    """Render edit form for web names."""
    row = st.session_state.selected_row_data

    with st.expander("✏️ Edit Web Name", expanded=True):
        with st.form("wn_form"):
            st.subheader(f"Editing: {row.get('DISPLAY_NAME')}")

            display_name = st.text_input("Display Name *", value=row.get('DISPLAY_NAME', ''))
            addr1 = st.text_input("Address Line 1 *", value=row.get('ADDRESS_LINE_1', ''))
            addr2 = st.text_input("Address Line 2", value=row.get('ADDRESS_LINE_2', '') or '')

            col1, col2, col3 = st.columns(3)
            with col1:
                city = st.text_input("City *", value=row.get('CITY', ''))
            with col2:
                state = st.text_input("State *", value=row.get('STATE', ''), max_chars=2)
            with col3:
                postal = st.text_input("Postal Code *", value=row.get('POSTAL_CODE', ''))

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Update", type="primary")
            with col2:
                cancelled = st.form_submit_button("❌ Cancel")

            if submitted:
                errors = []
                if not display_name.strip():
                    errors.append("Display Name is required")
                if not addr1.strip():
                    errors.append("Address Line 1 is required")
                if not city.strip():
                    errors.append("City is required")
                if not state.strip() or len(state.strip()) != 2:
                    errors.append("State must be 2 characters")
                if not postal.strip():
                    errors.append("Postal Code is required")

                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    updates = {
                        'DISPLAY_NAME': display_name.strip(),
                        'ADDRESS_LINE_1': addr1.strip(),
                        'ADDRESS_LINE_2': addr2.strip(),
                        'CITY': city.strip(),
                        'STATE': state.strip().upper(),
                        'POSTAL_CODE': postal.strip()
                    }
                    if update_web_name(row.get('BUSINESS_UNIT_CD'), updates):
                        st.success("Updated successfully!")
                        st.session_state.edit_mode = False
                        st.experimental_rerun()

            if cancelled:
                st.session_state.edit_mode = False
                st.session_state.selected_row_data = None
                st.experimental_rerun()

def main():
    """Main application."""
    initialize_session_state()
    render_header()
    render_sidebar()

    if st.session_state.selected_table == 'business_units':
        st.subheader("📊 Business Unit Details")
        render_business_units_table()
    else:
        st.subheader("🌐 Web Names")
        render_web_names_table()

    st.markdown("---")
    st.caption(f"🏢 Business Unit Manager v1.0 | Environment: **{get_environment_mode()}**")

if __name__ == "__main__":
    main()
