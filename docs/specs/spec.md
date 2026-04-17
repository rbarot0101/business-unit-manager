# Business Unit Web Name Manager - Project Specification

## Project Overview

A Streamlit web application that provides an interface for managing and updating business unit information stored in a Snowflake database. The application allows users to view, search, and update records across two related tables.

## Technical Stack

- **Frontend/Framework**: Streamlit
- **Database**: Snowflake
- **Connection Method**: `st.connection("snowflake")`
- **Language**: Python 3.8+

## Database Schema

### Tables

#### 1. ODS.PUBLIC.BUSINESS_UNIT_DETAILS
Primary table containing business unit information.

**Expected Columns** (to be confirmed with actual schema):
- `BUSINESS_UNIT_ID` - Primary key/identifier
- `BUSINESS_UNIT_NAME` - Name of the business unit
- `DESCRIPTION` - Business unit description
- `STATUS` - Active/Inactive status
- Additional metadata columns

#### 2. ODS.PUBLIC.BUSINESS_UNIT_WEB_NAME
Table containing web naming information for business units.

**Expected Columns** (to be confirmed with actual schema):
- `BUSINESS_UNIT_ID` - Foreign key to BUSINESS_UNIT_DETAILS
- `WEB_NAME` - Web-friendly name/URL slug
- `DOMAIN` - Associated domain
- `CREATED_DATE` - Creation timestamp
- `MODIFIED_DATE` - Last modification timestamp
- Additional metadata columns

### Relationships
- `BUSINESS_UNIT_WEB_NAME.BUSINESS_UNIT_ID` → `BUSINESS_UNIT_DETAILS.BUSINESS_UNIT_ID`

## Functional Requirements

### 1. Database Connection
- Use Streamlit's connection API: `st.connection("snowflake")`
- Connection configuration stored in `.streamlit/secrets.toml`
- Handle connection errors gracefully with user-friendly messages
- Implement connection pooling for performance

### 2. Data Viewing
- Display records from both tables in a structured format
- Implement pagination or virtual scrolling for large datasets
- Show related data (JOIN between tables) when appropriate
- Provide filtering and search capabilities:
  - Search by Business Unit ID
  - Search by Business Unit Name
  - Filter by Status
  - Search by Web Name

### 3. Data Editing

#### Business Unit Details Updates
- Allow editing of:
  - Business Unit Name
  - Description
  - Status (dropdown: Active/Inactive)
  - Other editable fields as per business rules
- Validate input data before submission
- Show confirmation before applying changes
- Display success/error messages after update

#### Business Unit Web Name Updates
- Allow editing of:
  - Web Name (with validation for URL-safe characters)
  - Domain
  - Other editable fields
- Auto-update `MODIFIED_DATE` timestamp
- Validate uniqueness of web names if required
- Show confirmation before applying changes

### 4. User Interface Requirements

#### Layout
- **Sidebar**: Navigation and filters
  - Table selection (Business Unit Details / Web Names)
  - Search/filter controls
  - Refresh data button
- **Main Area**: 
  - Data display (table/dataframe)
  - Edit form (when record selected)
  - Action buttons (Update, Cancel, Delete if applicable)
- **Header**: Application title and connection status

#### Components
- Use `st.dataframe()` or `st.data_editor()` for interactive data viewing
- Use `st.form()` for edit operations to batch inputs
- Use `st.selectbox()` for dropdown selections
- Use `st.text_input()` for text fields
- Use `st.button()` for actions with appropriate styling
- Use `st.success()`, `st.error()`, `st.warning()` for feedback messages

### 5. Data Validation

#### Business Unit Details
- Business Unit Name: Required, max length validation
- Description: Max length validation
- Status: Must be from predefined list

#### Business Unit Web Name
- Web Name: 
  - Required field
  - Must be URL-safe (alphanumeric, hyphens, underscores only)
  - Check for uniqueness if business rule requires
  - Length constraints (e.g., 3-100 characters)
- Domain: Valid domain format
- Business Unit ID: Must exist in BUSINESS_UNIT_DETAILS

### 6. Error Handling
- Database connection failures
- Query execution errors
- Validation errors
- Constraint violations (foreign key, unique)
- Network timeouts
- Insufficient permissions

## Non-Functional Requirements

### Security
- Store credentials in `.streamlit/secrets.toml` (never commit to git)
- Use parameterized queries to prevent SQL injection
- Implement role-based access if needed (read-only vs. editor)
- Audit trail: Log who made what changes and when
- Session management for user tracking

### Performance
- Use query caching with `@st.cache_data` for read operations
- Limit initial data load (e.g., 100 records with pagination)
- Implement efficient SQL queries with proper indexing
- Connection pooling to handle concurrent users

### Usability
- Intuitive navigation
- Clear labels and instructions
- Responsive design for different screen sizes
- Loading indicators for long operations
- Confirmation dialogs for destructive operations

### Maintainability
- Modular code structure
- Separate database operations from UI logic
- Configuration management (dev/prod environments)
- Logging for debugging and monitoring
- Documentation and inline comments

## Implementation Phases

### Phase 1: Setup & Read Operations
1. Project structure and dependencies
2. Snowflake connection setup
3. Basic UI layout
4. Display data from both tables
5. Implement search and filtering

### Phase 2: Update Operations
1. Build edit forms for BUSINESS_UNIT_DETAILS
2. Build edit forms for BUSINESS_UNIT_WEB_NAME
3. Implement validation logic
4. Add update queries
5. Error handling and user feedback

### Phase 3: Enhancement & Testing
1. Implement audit logging
2. Add batch operations if needed
3. Performance optimization
4. User acceptance testing
5. Documentation

## Configuration Files

### `.streamlit/secrets.toml`
```toml
[connections.snowflake]
account = "your-account"
user = "your-username"
password = "your-password"
warehouse = "your-warehouse"
database = "ODS"
schema = "PUBLIC"
role = "your-role"
```

### `requirements.txt`
```
streamlit>=1.28.0
snowflake-connector-python>=3.0.0
snowflake-snowpark-python>=1.0.0
pandas>=2.0.0
```

## SQL Operations

### Read Operations
```sql
-- Get all business unit details
SELECT * FROM ODS.PUBLIC.BUSINESS_UNIT_DETAILS ORDER BY BUSINESS_UNIT_ID;

-- Get all web names with business unit info
SELECT 
    bd.BUSINESS_UNIT_ID,
    bd.BUSINESS_UNIT_NAME,
    wn.WEB_NAME,
    wn.DOMAIN,
    wn.MODIFIED_DATE
FROM ODS.PUBLIC.BUSINESS_UNIT_DETAILS bd
LEFT JOIN ODS.PUBLIC.BUSINESS_UNIT_WEB_NAME wn
    ON bd.BUSINESS_UNIT_ID = wn.BUSINESS_UNIT_ID
ORDER BY bd.BUSINESS_UNIT_ID;
```

### Update Operations
```sql
-- Update business unit details
UPDATE ODS.PUBLIC.BUSINESS_UNIT_DETAILS
SET 
    BUSINESS_UNIT_NAME = ?,
    DESCRIPTION = ?,
    STATUS = ?
WHERE BUSINESS_UNIT_ID = ?;

-- Update web name
UPDATE ODS.PUBLIC.BUSINESS_UNIT_WEB_NAME
SET 
    WEB_NAME = ?,
    DOMAIN = ?,
    MODIFIED_DATE = CURRENT_TIMESTAMP()
WHERE BUSINESS_UNIT_ID = ?;
```

## Success Criteria

1. Users can successfully connect to Snowflake database
2. Users can view records from both tables
3. Users can search and filter records efficiently
4. Users can update records with validation
5. All updates are reflected in the database immediately
6. Error messages are clear and actionable
7. Application is responsive and performs well with expected data volume
8. No security vulnerabilities (SQL injection, credential exposure)

## Future Enhancements (Out of Scope for v1)

- Bulk import/export functionality
- Advanced reporting and analytics
- Integration with other systems
- Version history/change tracking
- User role management
- Mobile optimization
- REST API for programmatic access
- Multi-language support
