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
    table_name = f"ODS.PUBLIC.{tables['business_unit_details']}"

    query = f"SELECT * FROM {table_name}"
    if search_term:
        query += f" WHERE STORE_CD ILIKE '%{search_term}%'"
    query += " ORDER BY STORE_CD"

    return session.sql(query).to_pandas()

@st.cache_data(ttl=300)
def get_web_names(search_term=None):
    """Fetch web name details with JOIN."""
    session = get_active_session()
    tables = get_table_names()
    bu_table = f"ODS.PUBLIC.{tables['business_unit_details']}"
    wn_table = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

    query = f"""
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

    if search_term:
        query += f" WHERE wn.DISPLAY_NAME ILIKE '%{search_term}%' OR wn.CITY ILIKE '%{search_term}%' OR CAST(wn.BUSINESS_UNIT_CD AS VARCHAR) LIKE '%{search_term}%'"
    query += " ORDER BY bd.STORE_CD"

    return session.sql(query).to_pandas()

def update_business_unit(store_cd, updates):
    """Update business unit record."""
    try:
        session = get_active_session()
        tables = get_table_names()
        table_name = f"ODS.PUBLIC.{tables['business_unit_details']}"

        set_clause = ", ".join([f"{col} = '{val}'" for col, val in updates.items()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE STORE_CD = '{store_cd}'"

        session.sql(query).collect()
        get_business_units.clear()
        get_web_names.clear()
        return True
    except Exception as e:
        st.error(f"Update failed: {str(e)}")
        return False

def update_web_name(business_unit_cd, updates):
    """Update web name record."""
    try:
        session = get_active_session()
        tables = get_table_names()
        table_name = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

        set_clause = ", ".join([f"{col} = '{val}'" for col, val in updates.items()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE BUSINESS_UNIT_CD = '{business_unit_cd}'"

        session.sql(query).collect()
        get_business_units.clear()
        get_web_names.clear()
        return True
    except Exception as e:
        st.error(f"Update failed: {str(e)}")
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

def render_header():
    """Render header."""
    col1, col2 = st.columns([4, 1])

    with col1:
        st.title("🏢 Business Unit Manager")

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

    st.session_state.selected_table = 'business_units' if table_option == "Business Unit Details" else 'web_names'

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Search")
    st.session_state.search_term = st.sidebar.text_input("Search records", value=st.session_state.search_term)

    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            get_business_units.clear()
            get_web_names.clear()
            st.session_state.last_refresh = datetime.now()
            st.rerun()

    with col2:
        if st.button("✖ Clear", use_container_width=True):
            st.session_state.selected_row_index = None
            st.session_state.selected_row_data = None
            st.session_state.edit_mode = False
            st.rerun()

def render_business_units_table():
    """Render business units table."""
    df = get_business_units(st.session_state.search_term)

    if df.empty:
        st.warning("No records found.")
        return

    st.info(f"Showing {len(df)} records")

    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=400,
        selection_mode="single-row",
        on_select="rerun"
    )

    if event.selection.rows:
        idx = event.selection.rows[0]
        st.session_state.selected_row_data = df.iloc[idx].to_dict()
        st.session_state.edit_mode = True
        st.success(f"Selected: {st.session_state.selected_row_data.get('STORE_CD')}")

    if st.session_state.edit_mode and st.session_state.selected_row_data:
        render_business_unit_form()

def render_web_names_table():
    """Render web names table."""
    df = get_web_names(st.session_state.search_term)

    if df.empty:
        st.warning("No records found.")
        return

    st.info(f"Showing {len(df)} records")

    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=400,
        selection_mode="single-row",
        on_select="rerun"
    )

    if event.selection.rows:
        idx = event.selection.rows[0]
        st.session_state.selected_row_data = df.iloc[idx].to_dict()
        st.session_state.edit_mode = True
        st.success(f"Selected: {st.session_state.selected_row_data.get('DISPLAY_NAME')}")

    if st.session_state.edit_mode and st.session_state.selected_row_data:
        render_web_name_form()

def render_business_unit_form():
    """Render edit form for business units."""
    row = st.session_state.selected_row_data

    with st.expander("✏️ Edit Business Unit", expanded=True):
        with st.form("bu_form"):
            st.subheader(f"Store: {row.get('STORE_CD')}")

            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Latitude", value=float(row.get('ADDR_LATITUDE', 0)), format="%.6f")
                open_date = st.date_input("Open Date", value=row.get('OPEN_DATE'))
            with col2:
                lon = st.number_input("Longitude", value=float(row.get('ADDR_LONGITUDE', 0)), format="%.6f")
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
                        'MARKETING_UPDATABLE': marketing
                    }
                    if update_business_unit(row.get('STORE_CD'), updates):
                        st.success("Updated successfully!")
                        st.session_state.edit_mode = False
                        st.rerun()

            if cancelled:
                st.session_state.edit_mode = False
                st.session_state.selected_row_data = None
                st.rerun()

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
                        st.rerun()

            if cancelled:
                st.session_state.edit_mode = False
                st.session_state.selected_row_data = None
                st.rerun()

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
