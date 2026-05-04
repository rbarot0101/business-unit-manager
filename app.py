"""Business Unit Manager - Streamlit Application

Main application for managing business unit information in Snowflake.
Connects to backup tables by default for safe development/testing.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from loguru import logger

# Import database operations
from src.database.snowflake_operations import (
    get_snowflake_connection,
    get_business_units,
    get_web_names,
    get_store_labels,
    update_business_unit,
    update_web_name,
)
from src.utils.search_transform import resolve_search_term

# Import validators
from src.utils.validators import (
    validate_web_name,
    validate_domain,
    validate_required_field
)

# Import configuration
from config.table_config import get_environment_mode, is_backup_mode, get_table_names

# Page configuration
st.set_page_config(
    page_title="Business Unit Manager",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize session state variables."""
    if 'selected_table' not in st.session_state:
        st.session_state.selected_table = 'business_units'

    if 'selected_row_index' not in st.session_state:
        st.session_state.selected_row_index = None

    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    if 'search_term' not in st.session_state:
        st.session_state.search_term = ""

    if 'show_confirmation' not in st.session_state:
        st.session_state.show_confirmation = False

    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()

    if 'selected_row_data' not in st.session_state:
        st.session_state.selected_row_data = None


@st.cache_data(ttl=60)  # Cache connection test for 1 minute
def test_connection():
    """Test Snowflake connection and return status."""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_TIMESTAMP()")
        result = cursor.fetchone()
        return True, "Connected", result[0] if result else None
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False, str(e), None


def render_header():
    """Render application header with connection status and mode indicator."""
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.title("🏢 Business Unit Manager")
        st.caption("Lead: Ram Barot - Lead Data Engineer | Enterprise & Data Analytics Team")

    with col2:
        # Environment mode indicator
        env_mode = get_environment_mode()
        if is_backup_mode():
            st.success(f"🔒 **{env_mode} MODE**")
        else:
            st.error(f"⚠️ **{env_mode} MODE**")

    with col3:
        # Connection status
        connected, msg, server_time = test_connection()
        if connected:
            st.success("✓ Connected")
            if server_time:
                st.caption(f"Server time: {server_time}")
        else:
            st.error(f"✗ {msg[:50]}...")
            if st.button("🔄 Retry Connection"):
                test_connection.clear()
                st.rerun()

    # Display last refresh time and record counts
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.caption(f"📅 Last refresh: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
    with col_info2:
        if connected:
            # Get record counts
            if st.session_state.selected_table == 'business_units':
                df = get_business_units()
                st.caption(f"📊 Total business units: {len(df)}")
            else:
                df = get_web_names()
                st.caption(f"📊 Total web names: {len(df)}")

    # Show which tables are being used
    tables = get_table_names()
    with st.expander("ℹ️ Table Information"):
        st.info(f"""
        **Business Unit Details:** `{tables['business_unit_details']}`
        **Web Names:** `{tables['business_unit_web_name']}`

        {'⚠️ You are working with BACKUP tables. Production data is safe.' if is_backup_mode() else '⚠️ WARNING: You are working with PRODUCTION tables!'}
        """)


def render_sidebar():
    """Render sidebar with table selection and search."""
    st.sidebar.header("Navigation")

    # Table selection
    table_option = st.sidebar.radio(
        "Select Table",
        options=["Business Unit Details", "Web Names"],
        key="table_radio"
    )

    # Update session state based on selection
    if table_option == "Business Unit Details":
        st.session_state.selected_table = 'business_units'
    else:
        st.session_state.selected_table = 'web_names'

    st.sidebar.markdown("---")

    # Search/Filter
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

    # Actions
    st.sidebar.subheader("Actions")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            # Clear all caches and update refresh time
            get_business_units.clear()
            get_web_names.clear()
            test_connection.clear()
            st.session_state.last_refresh = datetime.now()
            st.session_state.selected_row_index = None
            st.session_state.selected_row_data = None
            st.session_state.edit_mode = False
            st.success("✅ Data refreshed!")
            st.rerun()

    def _on_clear_click():
        st.session_state.selected_row_index = None
        st.session_state.selected_row_data = None
        st.session_state.edit_mode = False
        st.session_state.search_term = ""
        st.session_state["search_input"] = ""

    with col2:
        st.button("✖ Clear", use_container_width=True, on_click=_on_clear_click)

    st.sidebar.markdown("---")

    # Help section
    with st.sidebar.expander("ℹ️ Help & Tips"):
        st.markdown("""
        **How to use:**
        1. Select a table from the radio buttons above
        2. Use search to filter records
        3. Click on a row in the table to select it
        4. Edit form will appear below the table
        5. Make changes and click Update
        6. Click Cancel to discard changes

        **Search tips:**
        - Business Units: searches by Store Code
        - Web Names: searches by Display Name, City, or Business Unit Code
        - Search is case-insensitive

        **Important:**
        - You are currently in **{mode}** mode
        - All changes affect {tables} tables only
        - Data is cached for 5 minutes
        - Use Refresh button to see latest data

        **Keyboard shortcuts:**
        - `Ctrl+R` or `F5`: Refresh browser
        - `Escape`: Close expanded sections
        """.format(
            mode="BACKUP" if is_backup_mode() else "PRODUCTION",
            tables="backup (ZZZ_*_20260417)" if is_backup_mode() else "PRODUCTION"
        ))


def render_main_area():
    """Render main content area with data table and edit form."""
    try:
        if st.session_state.selected_table == 'business_units':
            st.subheader("📊 Business Unit Details")
            render_business_units_view()
        else:
            st.subheader("🌐 Web Names")
            render_web_names_view()
    except Exception as e:
        st.error(f"❌ Error rendering data: {str(e)}")
        logger.error(f"Error in render_main_area: {e}", exc_info=True)
        if st.button("🔄 Reload"):
            st.rerun()


def render_business_units_view():
    """Render business units table and edit form."""
    # Fetch data
    with st.spinner("Loading business unit data..."):
        df = get_business_units(st.session_state.search_term)

    if df.empty:
        st.warning("No records found. Try adjusting your search.")
        return

    # Display record count
    total_records = len(df)
    if st.session_state.search_term:
        st.info(f"Found {total_records} records matching '{st.session_state.search_term}'")
    else:
        st.info(f"Showing {total_records} records")

    # Configure column display
    column_config = {
        "STORE_CD": st.column_config.TextColumn(
            "Store Code",
            width="small",
            help="Unique store identifier"
        ),
        "ADDR_LATITUDE": st.column_config.NumberColumn(
            "Latitude",
            format="%.6f",
            width="small"
        ),
        "ADDR_LONGITUDE": st.column_config.NumberColumn(
            "Longitude",
            format="%.6f",
            width="small"
        ),
        "SUNDAY_OPEN": st.column_config.TextColumn(
            "Sun Open",
            width="small"
        ),
        "SUNDAY_CLOSE": st.column_config.TextColumn(
            "Sun Close",
            width="small"
        ),
        "MONDAY_OPEN": st.column_config.TextColumn(
            "Mon Open",
            width="small"
        ),
        "MONDAY_CLOSE": st.column_config.TextColumn(
            "Mon Close",
            width="small"
        ),
        "TUESDAY_OPEN": st.column_config.TextColumn(
            "Tue Open",
            width="small"
        ),
        "TUESDAY_CLOSE": st.column_config.TextColumn(
            "Tue Close",
            width="small"
        ),
        "WEDNESDAY_OPEN": st.column_config.TextColumn(
            "Wed Open",
            width="small"
        ),
        "WEDNESDAY_CLOSE": st.column_config.TextColumn(
            "Wed Close",
            width="small"
        ),
        "THURSDAY_OPEN": st.column_config.TextColumn(
            "Thu Open",
            width="small"
        ),
        "THURSDAY_CLOSE": st.column_config.TextColumn(
            "Thu Close",
            width="small"
        ),
        "FRIDAY_OPEN": st.column_config.TextColumn(
            "Fri Open",
            width="small"
        ),
        "FRIDAY_CLOSE": st.column_config.TextColumn(
            "Fri Close",
            width="small"
        ),
        "SATURDAY_OPEN": st.column_config.TextColumn(
            "Sat Open",
            width="small"
        ),
        "SATURDAY_CLOSE": st.column_config.TextColumn(
            "Sat Close",
            width="small"
        ),
        "OPEN_DATE": st.column_config.DateColumn(
            "Open Date",
            format="YYYY-MM-DD",
            width="medium"
        ),
        "CLOSE_DATE": st.column_config.DateColumn(
            "Close Date",
            format="YYYY-MM-DD",
            width="medium"
        ),
        "MARKETING_UPDATABLE": st.column_config.CheckboxColumn(
            "Marketing Updatable",
            width="small"
        )
    }

    # Display dataframe with selection and column configuration
    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config=column_config,
        selection_mode="single-row",
        on_select="rerun",
        key="business_units_table"
    )

    # Handle row selection
    if event.selection.rows:
        selected_row_idx = event.selection.rows[0]
        st.session_state.selected_row_index = selected_row_idx
        st.session_state.selected_row_data = df.iloc[selected_row_idx].to_dict()
        st.session_state.edit_mode = True
        st.success(f"✓ Selected Store Code: {st.session_state.selected_row_data.get('STORE_CD', 'N/A')}")

    # Edit form
    if st.session_state.edit_mode and st.session_state.selected_row_data:
        render_business_unit_edit_form()
    else:
        st.caption("👆 Click on a row to select it for editing")


def render_web_names_view():
    """Render web names table and edit form."""
    # Fetch data
    with st.spinner("Loading web name data..."):
        df = get_web_names(st.session_state.search_term)

    if df.empty:
        st.warning("No records found. Try adjusting your search.")
        return

    # Display record count
    total_records = len(df)
    if st.session_state.search_term:
        st.info(f"Found {total_records} records matching '{st.session_state.search_term}'")
    else:
        st.info(f"Showing {total_records} records")

    # Configure column display
    column_config = {
        "STORE_CD": st.column_config.TextColumn(
            "Store Code",
            width="small",
            help="Store code from business unit details"
        ),
        "BUSINESS_UNIT_CD": st.column_config.TextColumn(
            "Business Unit Code",
            width="medium",
            help="Unique business unit identifier"
        ),
        "DISPLAY_NAME": st.column_config.TextColumn(
            "Display Name",
            width="large",
            help="Public-facing name"
        ),
        "ADDRESS_LINE_1": st.column_config.TextColumn(
            "Address Line 1",
            width="large"
        ),
        "ADDRESS_LINE_2": st.column_config.TextColumn(
            "Address Line 2",
            width="medium"
        ),
        "CITY": st.column_config.TextColumn(
            "City",
            width="medium"
        ),
        "STATE": st.column_config.TextColumn(
            "State",
            width="small"
        ),
        "POSTAL_CODE": st.column_config.TextColumn(
            "Postal Code",
            width="small"
        )
    }

    # Display dataframe with selection and column configuration
    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=400,
        column_config=column_config,
        selection_mode="single-row",
        on_select="rerun",
        key="web_names_table"
    )

    # Handle row selection
    if event.selection.rows:
        selected_row_idx = event.selection.rows[0]
        st.session_state.selected_row_index = selected_row_idx
        st.session_state.selected_row_data = df.iloc[selected_row_idx].to_dict()
        st.session_state.edit_mode = True
        st.success(f"✓ Selected: {st.session_state.selected_row_data.get('DISPLAY_NAME', 'N/A')} ({st.session_state.selected_row_data.get('BUSINESS_UNIT_CD', 'N/A')})")

    # Edit form
    if st.session_state.edit_mode and st.session_state.selected_row_data:
        render_web_name_edit_form()
    else:
        st.caption("👆 Click on a row to select it for editing")


def render_business_unit_edit_form():
    """Render edit form for business unit details."""
    row_data = st.session_state.selected_row_data

    with st.expander("✏️ Edit Business Unit Details", expanded=True):
        with st.form("business_unit_form"):
            st.subheader(f"Editing Store: {row_data.get('STORE_CD', 'N/A')}")

            # Non-editable field
            st.text_input("Store Code", value=row_data.get('STORE_CD', ''), disabled=True)

            # Editable fields (key editable fields only - not all 38 columns)
            col1, col2 = st.columns(2)

            with col1:
                addr_lat = st.number_input(
                    "Latitude",
                    value=float(row_data.get('ADDR_LATITUDE', 0)) if row_data.get('ADDR_LATITUDE') else 0.0,
                    format="%.6f",
                    help="Address latitude"
                )

                open_date = st.date_input(
                    "Open Date",
                    value=row_data.get('OPEN_DATE'),
                    help="Store opening date"
                )

                marketing_updatable = st.checkbox(
                    "Marketing Updatable",
                    value=bool(row_data.get('MARKETING_UPDATABLE', False)),
                    help="Can be updated by marketing"
                )

            with col2:
                addr_lon = st.number_input(
                    "Longitude",
                    value=float(row_data.get('ADDR_LONGITUDE', 0)) if row_data.get('ADDR_LONGITUDE') else 0.0,
                    format="%.6f",
                    help="Address longitude"
                )

                close_date = st.date_input(
                    "Close Date",
                    value=row_data.get('CLOSE_DATE') if row_data.get('CLOSE_DATE') else None,
                    help="Store closing date (optional)"
                )

            # Store hours section
            st.markdown("**Store Hours**")

            open_col, close_col = st.columns(2)

            with open_col:
                sunday_open = st.text_input("Sunday Open", value=row_data.get('SUNDAY_OPEN', ''))
                monday_open = st.text_input("Monday Open", value=row_data.get('MONDAY_OPEN', ''))
                tuesday_open = st.text_input("Tuesday Open", value=row_data.get('TUESDAY_OPEN', ''))
                wednesday_open = st.text_input("Wednesday Open", value=row_data.get('WEDNESDAY_OPEN', ''))
                thursday_open = st.text_input("Thursday Open", value=row_data.get('THURSDAY_OPEN', ''))
                friday_open = st.text_input("Friday Open", value=row_data.get('FRIDAY_OPEN', ''))
                saturday_open = st.text_input("Saturday Open", value=row_data.get('SATURDAY_OPEN', ''))

            with close_col:
                sunday_close = st.text_input("Sunday Close", value=row_data.get('SUNDAY_CLOSE', ''))
                monday_close = st.text_input("Monday Close", value=row_data.get('MONDAY_CLOSE', ''))
                tuesday_close = st.text_input("Tuesday Close", value=row_data.get('TUESDAY_CLOSE', ''))
                wednesday_close = st.text_input("Wednesday Close", value=row_data.get('WEDNESDAY_CLOSE', ''))
                thursday_close = st.text_input("Thursday Close", value=row_data.get('THURSDAY_CLOSE', ''))
                friday_close = st.text_input("Friday Close", value=row_data.get('FRIDAY_CLOSE', ''))
                saturday_close = st.text_input("Saturday Close", value=row_data.get('SATURDAY_CLOSE', ''))

            # Form buttons
            col1, col2, col3 = st.columns([1, 1, 4])

            with col1:
                submitted = st.form_submit_button("💾 Update", use_container_width=True, type="primary")

            with col2:
                cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)

            # Handle form submission
            if submitted:
                # Validate inputs
                validation_errors = []

                # Basic validation for latitude/longitude
                if addr_lat < -90 or addr_lat > 90:
                    validation_errors.append("Latitude must be between -90 and 90")
                if addr_lon < -180 or addr_lon > 180:
                    validation_errors.append("Longitude must be between -180 and 180")

                if validation_errors:
                    for error in validation_errors:
                        st.error(f"❌ {error}")
                else:
                    # Prepare updates dictionary
                    updates = {
                        'ADDR_LATITUDE': addr_lat,
                        'ADDR_LONGITUDE': addr_lon,
                        'OPEN_DATE': open_date,
                        'CLOSE_DATE': close_date,
                        'MARKETING_UPDATABLE': marketing_updatable,
                        'SUNDAY_OPEN': sunday_open,
                        'SUNDAY_CLOSE': sunday_close,
                        'MONDAY_OPEN': monday_open,
                        'MONDAY_CLOSE': monday_close,
                        'TUESDAY_OPEN': tuesday_open,
                        'TUESDAY_CLOSE': tuesday_close,
                        'WEDNESDAY_OPEN': wednesday_open,
                        'WEDNESDAY_CLOSE': wednesday_close,
                        'THURSDAY_OPEN': thursday_open,
                        'THURSDAY_CLOSE': thursday_close,
                        'FRIDAY_OPEN': friday_open,
                        'FRIDAY_CLOSE': friday_close,
                        'SATURDAY_OPEN': saturday_open,
                        'SATURDAY_CLOSE': saturday_close,
                    }

                    # Perform update
                    with st.spinner("Updating business unit..."):
                        success = update_business_unit(
                            row_data.get('STORE_CD'),
                            updates
                        )

                        if success:
                            st.success("✅ Business unit updated successfully!")
                            st.session_state.selected_row_index = None
                            st.session_state.selected_row_data = None
                            st.session_state.edit_mode = False
                            st.session_state.last_refresh = datetime.now()
                            # Wait a moment for user to see success message
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Failed to update business unit. Check logs for details.")

            if cancelled:
                st.session_state.selected_row_index = None
                st.session_state.selected_row_data = None
                st.session_state.edit_mode = False
                st.rerun()


def render_web_name_edit_form():
    """Render edit form for web name details."""
    row_data = st.session_state.selected_row_data

    with st.expander("✏️ Edit Web Name Details", expanded=True):
        with st.form("web_name_form"):
            st.subheader(f"Editing: {row_data.get('DISPLAY_NAME', 'N/A')}")

            # Non-editable fields
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Store Code", value=row_data.get('STORE_CD', ''), disabled=True)
            with col2:
                st.text_input("Business Unit Code", value=row_data.get('BUSINESS_UNIT_CD', ''), disabled=True)

            # Editable fields
            display_name = st.text_input(
                "Display Name *",
                value=row_data.get('DISPLAY_NAME', ''),
                max_chars=200,
                help="Public-facing display name"
            )

            address_line_1 = st.text_input(
                "Address Line 1 *",
                value=row_data.get('ADDRESS_LINE_1', ''),
                max_chars=200,
                help="Primary address line"
            )

            address_line_2 = st.text_input(
                "Address Line 2",
                value=row_data.get('ADDRESS_LINE_2', '') if row_data.get('ADDRESS_LINE_2') else '',
                max_chars=200,
                help="Secondary address line (optional)"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                city = st.text_input(
                    "City *",
                    value=row_data.get('CITY', ''),
                    max_chars=100,
                    help="City name"
                )

            with col2:
                state = st.text_input(
                    "State *",
                    value=row_data.get('STATE', ''),
                    max_chars=2,
                    help="2-letter state code"
                )

            with col3:
                postal_code = st.text_input(
                    "Postal Code *",
                    value=row_data.get('POSTAL_CODE', ''),
                    max_chars=10,
                    help="ZIP/Postal code"
                )

            st.caption("* Required fields")

            # Form buttons
            col1, col2, col3 = st.columns([1, 1, 4])

            with col1:
                submitted = st.form_submit_button("💾 Update", use_container_width=True, type="primary")

            with col2:
                cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)

            # Handle form submission
            if submitted:
                # Validate required fields
                validation_errors = []

                is_valid, error_msg = validate_required_field(display_name, "Display Name", 200)
                if not is_valid:
                    validation_errors.append(error_msg)

                is_valid, error_msg = validate_required_field(address_line_1, "Address Line 1", 200)
                if not is_valid:
                    validation_errors.append(error_msg)

                is_valid, error_msg = validate_required_field(city, "City", 100)
                if not is_valid:
                    validation_errors.append(error_msg)

                is_valid, error_msg = validate_required_field(state, "State", 2)
                if not is_valid:
                    validation_errors.append(error_msg)
                elif len(state.strip()) != 2:
                    validation_errors.append("State must be exactly 2 characters")

                is_valid, error_msg = validate_required_field(postal_code, "Postal Code", 10)
                if not is_valid:
                    validation_errors.append(error_msg)

                if validation_errors:
                    for error in validation_errors:
                        st.error(f"❌ {error}")
                else:
                    # Prepare updates dictionary
                    updates = {
                        'DISPLAY_NAME': display_name.strip(),
                        'ADDRESS_LINE_1': address_line_1.strip(),
                        'ADDRESS_LINE_2': address_line_2.strip() if address_line_2 else '',
                        'CITY': city.strip(),
                        'STATE': state.strip().upper(),
                        'POSTAL_CODE': postal_code.strip(),
                    }

                    # Perform update
                    with st.spinner("Updating web name..."):
                        success = update_web_name(
                            row_data.get('BUSINESS_UNIT_CD'),
                            updates
                        )

                        if success:
                            st.success("✅ Web name updated successfully!")
                            st.session_state.selected_row_index = None
                            st.session_state.selected_row_data = None
                            st.session_state.edit_mode = False
                            st.session_state.last_refresh = datetime.now()
                            # Wait a moment for user to see success message
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Failed to update web name. Check logs for details.")

            if cancelled:
                st.session_state.selected_row_index = None
                st.session_state.selected_row_data = None
                st.session_state.edit_mode = False
                st.rerun()


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()

    # Render header
    render_header()

    # Render sidebar
    render_sidebar()

    # Render main content
    render_main_area()

    # Footer
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)

    with footer_col1:
        st.caption("🏢 Business Unit Manager v1.0")

    with footer_col2:
        mode = get_environment_mode()
        if is_backup_mode():
            st.caption(f"🔒 Environment: **{mode}** (Safe Mode)")
        else:
            st.caption(f"⚠️ Environment: **{mode}** (Live Data)")

    with footer_col3:
        st.caption(f"💾 Database: ODS.PUBLIC | User: BI_SYS_USR")


if __name__ == "__main__":
    main()
