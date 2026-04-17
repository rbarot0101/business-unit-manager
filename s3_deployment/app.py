"""
Business Unit Manager - S3 Deployment Version

Entry point for S3-based deployment in DataApp Hub.
This version is designed to be loaded dynamically from S3 and executed
within the Hub's application context.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional

# S3 apps receive Snowflake connection via context
# The Hub injects: st.session_state["snowflake_connection"]

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


@st.cache_resource
def get_snowflake_connection():
    """Get Snowflake connection using Streamlit's native connection management."""
    try:
        return st.connection("snowflake")
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_business_units(search_term: str = None) -> pd.DataFrame:
    """Fetch business unit details with optional search."""
    conn = get_snowflake_connection()
    if not conn:
        return pd.DataFrame()

    tables = get_table_names()
    table_name = f"ODS.PUBLIC.{tables['business_unit_details']}"

    query = f"SELECT * FROM {table_name}"

    if search_term:
        query += f" WHERE STORE_CD ILIKE '%{search_term}%'"

    query += " ORDER BY STORE_CD LIMIT 1000"

    try:
        df = conn.query(query, ttl="5m")
        return df
    except Exception as e:
        st.error(f"Error fetching business units: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_web_names(search_term: str = None) -> pd.DataFrame:
    """Fetch web names with business unit join."""
    conn = get_snowflake_connection()
    if not conn:
        return pd.DataFrame()

    tables = get_table_names()
    bu_table = f"ODS.PUBLIC.{tables['business_unit_details']}"
    wn_table = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

    query = f"""
        SELECT
            w.*
        FROM {wn_table} w
    """

    if search_term:
        query += f" WHERE w.DISPLAY_NAME ILIKE '%{search_term}%' OR w.BUSINESS_UNIT_CD ILIKE '%{search_term}%' OR w.CITY ILIKE '%{search_term}%'"

    query += " ORDER BY w.BUSINESS_UNIT_CD LIMIT 1000"

    try:
        df = conn.query(query, ttl="5m")
        return df
    except Exception as e:
        st.error(f"Error fetching web names: {e}")
        return pd.DataFrame()


def update_business_unit(store_cd: str, updates: dict) -> tuple[bool, str]:
    """Update business unit record."""
    conn = get_snowflake_connection()
    if not conn:
        return False, "No database connection available"

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
            escaped_val = val.replace("'", "''")
            set_parts.append(f"{col} = '{escaped_val}'")

    set_clause = ", ".join(set_parts)
    query = f"UPDATE {table_name} SET {set_clause} WHERE STORE_CD = '{store_cd}'"

    try:
        # For UPDATE/INSERT/DELETE, use the raw connection
        cursor = conn._instance.cursor()
        cursor.execute(query)
        conn._instance.commit()  # Commit the transaction
        cursor.close()
        return True, "Update successful"
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        st.error(f"**Full Error:**")
        st.code(error_details)
        st.error(f"**Query:**")
        st.code(query)
        return False, f"Update failed: {str(e)}"


def update_web_name(business_unit_cd: str, updates: dict) -> tuple[bool, str]:
    """Update web name record."""
    conn = get_snowflake_connection()
    if not conn:
        return False, "No database connection available"

    tables = get_table_names()
    table_name = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

    # Build SET clause
    set_parts = []
    for col, val in updates.items():
        if val is None:
            set_parts.append(f"{col} = NULL")
        elif isinstance(val, str):
            escaped_val = val.replace("'", "''")
            set_parts.append(f"{col} = '{escaped_val}'")

    set_clause = ", ".join(set_parts)
    query = f"UPDATE {table_name} SET {set_clause} WHERE BUSINESS_UNIT_CD = '{business_unit_cd}'"

    try:
        # For UPDATE/INSERT/DELETE, use the raw connection
        cursor = conn._instance.cursor()
        cursor.execute(query)
        conn._instance.commit()  # Commit the transaction
        cursor.close()
        return True, "Update successful"
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        st.error(f"**Full Error:**")
        st.code(error_details)
        st.error(f"**Query:**")
        st.code(query)
        return False, f"Update failed: {str(e)}"


def validate_latitude(lat: float) -> bool:
    """Validate latitude is in valid range."""
    return -90 <= lat <= 90


def validate_longitude(lon: float) -> bool:
    """Validate longitude is in valid range."""
    return -180 <= lon <= 180


def initialize_session_state():
    """Initialize session state variables."""
    if 'selected_table' not in st.session_state:
        st.session_state.selected_table = 'business_units'
    if 'selected_row_data' not in st.session_state:
        st.session_state.selected_row_data = None
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'search_term' not in st.session_state:
        st.session_state.search_term = ""
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


def render_sidebar():
    """Render sidebar navigation."""
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
    st.session_state.search_term = st.sidebar.text_input("Search records", value=st.session_state.search_term)

    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            get_business_units.clear()
            get_web_names.clear()
            st.rerun()

    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.selected_row_data = None
            st.session_state.edit_mode = False
            st.session_state.search_term = ""
            st.session_state.bu_selected_option = "-- Select a record --"
            st.session_state.wn_selected_option = "-- Select a record --"
            get_business_units.clear()
            get_web_names.clear()
            st.rerun()


def render_business_units_table():
    """Render business units table with selection."""
    df = get_business_units(st.session_state.search_term)

    if df.empty:
        st.warning("No records found.")
        return

    st.info(f"Showing {len(df)} records")
    st.dataframe(df, use_container_width=True, height=400)

    st.markdown("---")
    st.markdown("**📝 Select a record to edit:**")
    st.caption("👇 Use the dropdown below to select a record")

    if not df.empty:
        options = ["-- Select a record --"] + [
            f"{row['STORE_CD']} - Lat: {row.get('ADDR_LATITUDE', 'N/A')}, Lon: {row.get('ADDR_LONGITUDE', 'N/A')}"
            for _, row in df.iterrows()
        ]

        # Auto-select if only 1 record
        current_index = 0
        if len(df) == 1:
            current_index = 1
            auto_selected_option = options[1]
            if st.session_state.bu_selected_option != auto_selected_option:
                st.session_state.bu_selected_option = auto_selected_option
                st.session_state.selected_row_data = df.iloc[0].to_dict()
                st.session_state.edit_mode = True
        elif st.session_state.bu_selected_option != "-- Select a record --":
            for idx, opt in enumerate(options):
                if opt == st.session_state.bu_selected_option:
                    current_index = idx
                    break
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
            store_cd = selected_option.split(" - ")[0]
            selected_row = df[df['STORE_CD'] == store_cd]
            if not selected_row.empty:
                st.session_state.selected_row_data = selected_row.iloc[0].to_dict()
                st.session_state.edit_mode = True
                st.session_state.bu_selected_option = selected_option
                st.success(f"Selected: {store_cd}")
        else:
            st.session_state.selected_row_data = None
            st.session_state.edit_mode = False
            st.session_state.bu_selected_option = "-- Select a record --"

    if st.session_state.edit_mode and st.session_state.selected_row_data:
        render_business_unit_form()


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
            submitted = col1.form_submit_button("Update", use_container_width=True)
            cancelled = col2.form_submit_button("Cancel", use_container_width=True)

            if cancelled:
                st.session_state.edit_mode = False
                st.session_state.selected_row_data = None
                st.session_state.bu_selected_option = "-- Select a record --"
                st.rerun()

            if submitted:
                # Validation
                if not validate_latitude(lat):
                    st.error("Latitude must be between -90 and 90")
                    return
                if not validate_longitude(lon):
                    st.error("Longitude must be between -180 and 180")
                    return

                # Update
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

                success, message = update_business_unit(row['STORE_CD'], updates)
                if success:
                    st.success(message)
                    get_business_units.clear()
                    st.session_state.edit_mode = False
                    st.session_state.selected_row_data = None
                    st.rerun()
                else:
                    st.error(message)


def render_web_names_table():
    """Render web names table with selection."""
    df = get_web_names(st.session_state.search_term)

    if df.empty:
        st.warning("No records found.")
        return

    st.info(f"Showing {len(df)} records")
    st.dataframe(df, use_container_width=True, height=400)

    st.markdown("---")
    st.markdown("**📝 Select a record to edit:**")
    st.caption("👇 Use the dropdown below to select a record")

    if not df.empty:
        options = ["-- Select a record --"] + [
            f"{row.get('BUSINESS_UNIT_CD', 'N/A')} - {row.get('DISPLAY_NAME', 'N/A')} ({row.get('CITY', 'N/A')})"
            for _, row in df.iterrows()
        ]

        # Auto-select if only 1 record
        current_index = 0
        if len(df) == 1:
            current_index = 1
            auto_selected_option = options[1]
            if st.session_state.wn_selected_option != auto_selected_option:
                st.session_state.wn_selected_option = auto_selected_option
                st.session_state.selected_row_data = df.iloc[0].to_dict()
                st.session_state.edit_mode = True
        elif st.session_state.wn_selected_option != "-- Select a record --":
            for idx, opt in enumerate(options):
                if opt == st.session_state.wn_selected_option:
                    current_index = idx
                    break
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
            business_unit_cd = selected_option.split(" - ")[0]
            selected_row = df[df['BUSINESS_UNIT_CD'] == business_unit_cd]
            if not selected_row.empty:
                st.session_state.selected_row_data = selected_row.iloc[0].to_dict()
                st.session_state.edit_mode = True
                st.session_state.wn_selected_option = selected_option
                st.success(f"Selected: {selected_row.iloc[0].get('DISPLAY_NAME')}")
        else:
            st.session_state.selected_row_data = None
            st.session_state.edit_mode = False
            st.session_state.wn_selected_option = "-- Select a record --"

    if st.session_state.edit_mode and st.session_state.selected_row_data:
        render_web_name_form()


def render_web_name_form():
    """Render edit form for web names."""
    row = st.session_state.selected_row_data

    with st.expander("✏️ Edit Web Name", expanded=True):
        with st.form("wn_form"):
            st.subheader(f"Business Unit: {row.get('BUSINESS_UNIT_CD')}")

            display_name = st.text_input("Display Name", value=row.get('DISPLAY_NAME', ''))
            addr1 = st.text_input("Address Line 1", value=row.get('ADDRESS_LINE_1', ''))
            addr2 = st.text_input("Address Line 2", value=row.get('ADDRESS_LINE_2', ''))

            col1, col2, col3 = st.columns(3)
            with col1:
                city = st.text_input("City", value=row.get('CITY', ''))
            with col2:
                state = st.text_input("State", value=row.get('STATE', ''), max_chars=2)
            with col3:
                postal = st.text_input("Postal Code", value=row.get('POSTAL_CODE', ''))

            col1, col2 = st.columns(2)
            submitted = col1.form_submit_button("Update", use_container_width=True)
            cancelled = col2.form_submit_button("Cancel", use_container_width=True)

            if cancelled:
                st.session_state.edit_mode = False
                st.session_state.selected_row_data = None
                st.session_state.wn_selected_option = "-- Select a record --"
                st.rerun()

            if submitted:
                # Validation
                if not display_name:
                    st.error("Display Name is required")
                    return
                if not addr1:
                    st.error("Address Line 1 is required")
                    return
                if not city:
                    st.error("City is required")
                    return
                if not state or len(state) != 2:
                    st.error("State must be exactly 2 characters")
                    return
                if not postal:
                    st.error("Postal Code is required")
                    return

                # Update
                updates = {
                    'DISPLAY_NAME': display_name,
                    'ADDRESS_LINE_1': addr1,
                    'ADDRESS_LINE_2': addr2,
                    'CITY': city,
                    'STATE': state.upper(),
                    'POSTAL_CODE': postal
                }

                success, message = update_web_name(row['BUSINESS_UNIT_CD'], updates)
                if success:
                    st.success(message)
                    get_web_names.clear()
                    st.session_state.edit_mode = False
                    st.session_state.selected_row_data = None
                    st.rerun()
                else:
                    st.error(message)


def main():
    """Main application entry point for S3 deployment."""
    # Initialize session state
    initialize_session_state()

    # Render header
    render_header()

    # Render sidebar
    render_sidebar()

    # Render selected table
    if st.session_state.selected_table == 'business_units':
        render_business_units_table()
    else:
        render_web_names_table()

    # Footer
    st.markdown("---")
    st.caption(f"Business Unit Manager v1.0.0 | Mode: {get_environment_mode()}")


# Entry point for S3 app execution
if __name__ == "__main__":
    main()
