# Business Unit Manager - Implementation Plan

## Context

This implementation plan covers building the Streamlit user interface for the Business Unit Web Name application. The application will connect to Snowflake and allow users to manage records in two tables:
- `ODS.PUBLIC.BUSINESS_UNIT_DETAILS` - Core business unit information
- `ODS.PUBLIC.BUSINESS_UNIT_WEB_NAME` - Web naming and domain information

### What's Already Built

The foundational infrastructure is complete:

1. **Snowflake Configuration** (`config/snowflake_config.py`)
   - RSA key-based authentication
   - Connection parameter management
   - Configuration loading from `.streamlit/secrets.toml`

2. **Database Operations** (`src/database/snowflake_operations.py`)
   - `get_business_units(search_term)` - fetches business unit details with optional search
   - `get_web_names(search_term)` - fetches web names with JOIN to business units
   - `update_business_unit(business_unit_id, updates)` - updates business unit records
   - `update_web_name(business_unit_id, updates)` - updates web name records with auto MODIFIED_DATE
   - All queries use caching (@st.cache_data with 5-minute TTL)
   - All updates use parameterized queries for SQL injection prevention
   - Automatic cache clearing after updates

3. **Input Validators** (`src/utils/validators.py`)
   - `validate_web_name()` - ensures URL-safe characters only (alphanumeric, hyphens, underscores)
   - `validate_domain()` - validates domain format
   - `validate_required_field()` - checks required fields with max length

4. **Configuration Files**
   - `.streamlit/secrets.toml` - Snowflake credentials (already configured with RSA key)
   - `requirements.txt` - All dependencies specified
   - `.gitignore` - Proper exclusions for secrets and keys

### What Needs to Be Built

1. **Configuration for table switching** (`config/table_config.py`):
   - Toggle between backup and production tables
   - Environment-aware table name resolution

2. **Update existing database operations** (`src/database/snowflake_operations.py`):
   - Modify all queries to use configurable table names
   - Support switching between backup (ZZZ_*_20260417) and production tables

3. **Main Streamlit application** (`app.py`):
   - User interface layout (header, sidebar, main area)
   - Data display for both tables with search/filter
   - Row selection and edit forms
   - Update handlers with validation
   - Error handling and user feedback
   - Connection status monitoring
   - Environment indicator showing BACKUP vs PRODUCTION mode

---

## Implementation Plan

### 1. Application Architecture

**Type**: Single-page application with dynamic content
**Layout**: Header + Sidebar + Main Area
**State Management**: Streamlit session_state for tracking user selections and edit mode

**Session State Variables**:
- `selected_table` - Current table view ("business_units" or "web_names")
- `selected_row_index` - Index of selected row for editing (None if no selection)
- `edit_mode` - Boolean indicating if edit form is active
- `search_term` - Current search filter text
- `show_confirmation` - Boolean for update confirmation dialog
- `last_refresh` - Timestamp of last data refresh

### 2. Page Layout Structure

#### Header Section
- Application title: "Business Unit Manager"
- Connection status indicator using `st.status()` (green = connected, red = error)
- Last refresh timestamp
- Quick stats: Total records count for current table view

#### Sidebar Section
- **Table Selection**: Radio buttons to switch between:
  - "Business Unit Details"
  - "Web Names"
- **Search/Filter**: Text input for filtering records
- **Actions**:
  - "Refresh Data" button (clears cache and reloads)
  - "Clear Selection" button (deselects current row)
- **Help/Info**: Expandable section with usage instructions

#### Main Area
- **Data Table**: Interactive dataframe using `st.dataframe()` with single-row selection
- **Edit Form**: Appears below table when a row is selected
  - Wrapped in `st.expander()` for clean UI
  - Uses `st.form()` to batch inputs
  - Pre-filled with current values
  - Validation feedback inline
- **Feedback Area**: Success/error messages using `st.success()`, `st.error()`, `st.warning()`

### 3. Data Display Implementation

#### Business Unit Details Table
**Columns to display**:
STORE_CD ,
	ADDR_LATITUDE ,
	ADDR_LONGITUDE ,
	SUNDAY_OPEN ,
	SUNDAY_CLOSE ,
	MONDAY_OPEN ,
	MONDAY_CLOSE ,
	TUESDAY_OPEN ,
	TUESDAY_CLOSE ,
	WEDNESDAY_OPEN ,
	WEDNESDAY_CLOSE ,
	THURSDAY_OPEN ,
	THURSDAY_CLOSE ,
	FRIDAY_OPEN ,
	FRIDAY_CLOSE ,
	SATURDAY_OPEN ,
	SATURDAY_CLOSE ,
	OPEN_DATE DATE,
	CLOSE_DATE DATE,
	MARKETING_UPDATABLE 

**Features**:
- `use_container_width=True` for responsive layout
- `hide_index=True` for cleaner appearance
- `selection_mode="single-row"` for edit selection
- `on_select="rerun"` to trigger form display
- Column configuration for better formatting

#### Web Names Table
**Columns to display** (with JOIN):
BUSINESS_UNIT_CD ,
	DISPLAY_NAME ,
	ADDRESS_LINE_1 ,
	ADDRESS_LINE_2 ,
	CITY ,
	STATE ,
	POSTAL_CODE ,

**Features**:
- Same interactive features as Business Unit table
- Date formatting for timestamp columns
- Empty state handling with friendly message

### 4. Edit Form Design

#### Business Unit Edit Form
**Editable Fields**:
- Business Unit Name (text input, required, max length validation)
- Description (text area, optional, max length validation)
- Status (selectbox with predefined options: Active, Inactive)

**Non-editable Fields** (displayed with `disabled=True`):
- Business Unit ID

**Layout**:
- Form title: "Edit Business Unit: {NAME}"
- Fields in logical order
- Help text for each field explaining constraints
- Two-column button layout: [Update] [Cancel]

#### Web Name Edit Form
**Editable Fields**:
- Web Name (text input, required, URL-safe validation)
- Domain (text input, required, domain format validation)

**Non-editable Fields** (displayed with `disabled=True`):
- Business Unit ID
- Business Unit Name
- Modified Date (auto-updated on save)

**Layout**:
- Form title: "Edit Web Name for: {BUSINESS_UNIT_NAME}"
- Validation hints in help text
- Real-time validation feedback
- Two-column button layout: [Update] [Cancel]

### 5. User Flow

#### Viewing Data
1. User opens application → loads Business Unit Details by default
2. Data displayed in interactive table with search box
3. User can type in search box → results filter in real-time
4. User can switch tables via sidebar radio buttons
5. Empty states show helpful message: "No records found. Try adjusting your search."

#### Editing Records
1. User clicks on a row in the table → row highlights
2. Edit form appears below table in expanded state
3. Form is pre-filled with current values
4. User modifies fields → validation happens on input
5. Invalid inputs show error message above field
6. User clicks "Update" → validation runs
7. If valid → confirmation dialog appears: "Are you sure you want to update this record?"
8. User confirms → database update executes
9. Success message appears → cache clears → data refreshes → form closes → selection clears
10. User can click "Cancel" at any time → form closes → selection clears

#### Search/Filter
1. User types in sidebar search box
2. Search term applies to multiple columns:
   - Business Units: BUSINESS_UNIT_ID, BUSINESS_UNIT_NAME
   - Web Names: BUSINESS_UNIT_ID, BUSINESS_UNIT_NAME, WEB_NAME
3. Table updates with filtered results
4. Search is case-insensitive
5. Shows count: "Showing X of Y records"

### 6. Error Handling & Feedback

#### Connection Errors
- Display in header with red status badge
- Show error message: "Unable to connect to Snowflake. Please check your connection."
- Provide "Retry Connection" button
- Disable all edit functionality when disconnected

#### Validation Errors
- Display inline above form fields with `st.error()`
- Prevent form submission until all validations pass
- Keep form open with user's changes intact
- Specific messages for each validation type:
  - "Web name must contain only letters, numbers, hyphens, and underscores"
  - "Domain format is invalid. Example: example.com"
  - "This field is required"

#### Update Errors
- Display error message with details
- Keep form open with user's changes
- Offer "Retry" option
- Log error details for debugging

#### Success Feedback
- Green success message: "Business unit updated successfully!"
- Auto-dismiss after 3 seconds
- Form closes automatically
- Data refreshes to show changes

### 7. Code Organization

Structure `app.py` with the following organization:

```python
# Imports
import streamlit as st
import pandas as pd
from datetime import datetime
from src.database import get_business_units, get_web_names, update_business_unit, update_web_name
from src.utils import validate_web_name, validate_domain, validate_required_field

# Page Configuration
st.set_page_config(
    page_title="Business Unit Manager",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper Functions
def initialize_session_state()
def test_connection()
def render_header()
def render_sidebar()
def render_business_units_table(df, search_term)
def render_web_names_table(df, search_term)
def render_business_unit_edit_form(selected_row)
def render_web_name_edit_form(selected_row)
def handle_business_unit_update(business_unit_id, updates)
def handle_web_name_update(business_unit_id, updates)

# Main Function
def main()

# Entry Point
if __name__ == "__main__":
    main()
```

### 8. Implementation Phases

#### Phase 0: Database Backup & Development Setup (CRITICAL - Do First!)
**Duration**: 30 minutes

**IMPORTANT**: This is a PRODUCTION environment. All development and testing will be done on BACKUP tables. Do NOT touch production tables until final go-live.

**Backup Table Naming Convention**: `ZZZ_TABLENAME_YYYYMMDD`

**Backup Tasks**:
1. Create backup table for BUSINESS_UNIT_DETAILS:
   ```sql
   CREATE TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417 AS
   SELECT * FROM ODS.PUBLIC.BUSINESS_UNIT_DETAILS;
   ```

2. Create backup table for BUSINESS_UNIT_WEB_NAME:
   ```sql
   CREATE TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_WEB_NAME_20260417 AS
   SELECT * FROM ODS.PUBLIC.BUSINESS_UNIT_WEB_NAME;
   ```

3. Verify backup row counts match originals:
   ```sql
   SELECT 'BUSINESS_UNIT_DETAILS (PROD)' AS TABLE_NAME, COUNT(*) AS ROW_COUNT 
   FROM ODS.PUBLIC.BUSINESS_UNIT_DETAILS
   UNION ALL
   SELECT 'ZZZ_BUSINESS_UNIT_DETAILS_20260417 (BACKUP)', COUNT(*) 
   FROM ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417
   UNION ALL
   SELECT 'BUSINESS_UNIT_WEB_NAME (PROD)', COUNT(*) 
   FROM ODS.PUBLIC.BUSINESS_UNIT_WEB_NAME
   UNION ALL
   SELECT 'ZZZ_BUSINESS_UNIT_WEB_NAME_20260417 (BACKUP)', COUNT(*) 
   FROM ODS.PUBLIC.ZZZ_BUSINESS_UNIT_WEB_NAME_20260417;
   ```

4. Document backup timestamp and row counts

**Development Strategy**:
- **ALL development work** (Phases 1-5) will use the ZZZ backup tables
- Add a configuration setting to toggle between BACKUP and PRODUCTION tables
- Default to BACKUP mode during development
- Only switch to PRODUCTION mode after complete testing and approval

**Configuration File to Create** (`config/table_config.py`):
```python
# Table configuration for development vs production
USE_BACKUP_TABLES = True  # Set to False only for production deployment
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
```

**Note**: DO NOT proceed to Phase 1 without:
1. Creating backup tables
2. Verifying row counts match
3. Creating table_config.py
4. Updating database operations to use configurable table names

---

#### Phase 1: Configuration & Basic Structure (2-3 hours)
- Create `config/table_config.py` with backup/production toggle
- Update `src/database/snowflake_operations.py` to use configurable table names from table_config
- Verify updated queries work with backup tables (ZZZ_BUSINESS_UNIT_DETAILS_20260417, ZZZ_BUSINESS_UNIT_WEB_NAME_20260417)
- Create `app.py` with page configuration
- Implement `initialize_session_state()`
- Build `render_header()` with title, connection status, and BACKUP/PRODUCTION mode indicator
- Build `render_sidebar()` with table selection and search input
- Create `main()` function to orchestrate the flow
- Test: App loads, connects to BACKUP tables, sidebar works, can switch between tables

#### Phase 2: Data Display (2-3 hours)
- Implement `render_business_units_table()` with `st.dataframe()`
- Implement `render_web_names_table()` with JOIN data
- Add search/filter logic to both table functions
- Handle empty states
- Add loading indicators with `st.spinner()`
- Test: Data loads, search filters work, empty states display correctly

#### Phase 3: Row Selection & Forms (3-4 hours)
- Implement row selection handling via session state
- Create `render_business_unit_edit_form()` with all fields
- Create `render_web_name_edit_form()` with all fields
- Pre-fill forms with selected row data
- Add Cancel button handlers
- Test: Can select row, form appears, cancel works, form closes

#### Phase 4: Update Logic & Validation (2-3 hours)
- Integrate validators into form fields
- Implement `handle_business_unit_update()` with validation
- Implement `handle_web_name_update()` with validation
- Add confirmation dialogs before updates
- Implement success/error feedback
- Clear cache after successful updates
- Test: Validation works, updates succeed, errors are caught, cache clears

#### Phase 5: Polish & Error Handling (1-2 hours)
- Implement connection status monitoring in header
- Add comprehensive error handling for all database operations
- Add loading states and progress indicators
- Implement last refresh timestamp
- Add record count displays
- Polish UI styling and spacing
- Test: All error scenarios handled gracefully, UI is responsive

**Total Estimated Time**: 9-14 hours

### 9. Key Design Decisions

#### Why `st.dataframe()` over `st.data_editor()`?
- Better control over validation with explicit forms
- Clearer user intent (select then edit, not inline editing)
- Easier to implement confirmation dialogs
- Better audit trail (explicit update action)

#### Why form submission over inline editing?
- Batch validation of all fields together
- User can review all changes before submitting
- Clearer distinction between viewing and editing
- Prevents accidental updates

#### Why session state over query parameters?
- Simpler implementation for single-page app
- Better form state management
- No URL pollution
- Better handling of complex state like selected row data

#### Why 5-minute cache TTL?
- Balance between performance and data freshness
- Manual refresh available for immediate updates
- Cache auto-clears after writes for consistency
- Typical business data doesn't change frequently

### 10. Testing & Verification Approach

#### Manual Testing Checklist
- [ ] Application starts without errors
- [ ] Connection to Snowflake succeeds
- [ ] Business Unit table loads with data
- [ ] Web Names table loads with data
- [ ] Search/filter works for both tables
- [ ] Can select a row in Business Unit table
- [ ] Edit form appears with correct data
- [ ] Can modify Business Unit fields
- [ ] Validation prevents invalid Business Unit updates
- [ ] Successful Business Unit update shows confirmation
- [ ] Data refreshes after Business Unit update
- [ ] Can select a row in Web Names table
- [ ] Can modify Web Name fields
- [ ] Validation prevents invalid Web Name updates (URL-safe check)
- [ ] Validation prevents invalid Domain updates
- [ ] Successful Web Name update shows confirmation
- [ ] MODIFIED_DATE updates automatically
- [ ] Cancel button closes form without saving
- [ ] Clear Selection button works
- [ ] Refresh Data button clears cache and reloads
- [ ] Error handling works for connection failures
- [ ] Error handling works for validation failures
- [ ] Error handling works for update failures
- [ ] Empty search results show appropriate message
- [ ] Connection status displays correctly in header
- [ ] Last refresh timestamp updates

#### Unit Tests (Optional for Phase 1)
- Test session state initialization
- Test validation function integration
- Test update handlers with mocked database calls
- Test search filter logic

#### Integration Tests (Optional for Phase 1)
- Full update flow with test data in Snowflake
- Cache clearing verification
- Concurrent user scenarios

### 11. Critical Files

**Files to Create**:
- `config/table_config.py` - Environment configuration for backup vs production tables
- `app.py` - Main Streamlit application (primary implementation)

**Files to Update**:
- `src/database/snowflake_operations.py` - Modify to use configurable table names
- `CLAUDE.md` - Add section on running the app, development workflow, and backup/production switching

**Files to Reference** (already exist, no changes needed):
- `src/utils/validators.py` - Validation functions
- `.streamlit/secrets.toml` - Database credentials

### 12. Go-Live Procedure

Once all testing is complete and approved on backup tables:

1. **Final Verification on Backup Tables**:
   - Complete all items in testing checklist (Section 10)
   - Document any changes made during testing
   - Get user approval to proceed

2. **Switch to Production Tables**:
   - Open `config/table_config.py`
   - Change `USE_BACKUP_TABLES = True` to `USE_BACKUP_TABLES = False`
   - Save the file
   - Restart the Streamlit application

3. **Production Smoke Test**:
   - Verify connection to production tables
   - View records (read-only test)
   - Select a record and view edit form (but DO NOT update yet)
   - Verify all data displays correctly

4. **First Production Update** (with supervision):
   - Make a single, non-critical update on a test record
   - Verify the update succeeded
   - Verify no unintended side effects

5. **Monitor Initial Usage**:
   - Watch for any errors in first 24 hours
   - Keep backup tables intact for rollback if needed

6. **Cleanup** (after 1 week of stable operation):
   - Keep backup tables in ODS.PUBLIC for emergency rollback
   - Optional: Drop backup tables if storage is a concern and no rollback is needed:
     ```sql
     -- Only after confirming production is stable
     DROP TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417;
     DROP TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_WEB_NAME_20260417;
     ```
   - Recommended: Keep backups for at least 30 days in ODS.PUBLIC

---

## Next Steps

Once this plan is approved:
1. Create `app.py` following the phase-by-phase approach
2. Test each phase before moving to the next
3. Iterate on UI/UX based on user feedback
4. Consider future enhancements (audit logging, batch operations, etc.)

## Questions to Resolve Before Implementation

1. **Table Schema Confirmation**: Do we need to query the actual table schemas to see all available columns beyond the assumed ones?
2. **Status Field Values**: What are the actual valid values for the STATUS field in BUSINESS_UNIT_DETAILS?
3. **Additional Editable Fields**: Are there other fields in either table that should be editable?
4. **Permissions**: Does the BI_SYS_USR role have UPDATE permissions on both tables?
5. **Audit Requirements**: Do we need to log who made changes and when (beyond what's in the database)?
6. **Pagination**: Should we implement pagination/limits for large datasets, or is the full dataset small enough to display?
