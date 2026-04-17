# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Streamlit web application for managing business unit information in Snowflake. Users can view, search, and update records in two tables:
- `ODS.PUBLIC.BUSINESS_UNIT_DETAILS` - Core business unit information
- `ODS.PUBLIC.BUSINESS_UNIT_WEB_NAME` - Web naming/domain information

**Key Technologies**: Streamlit, Snowflake (via `st.connection("snowflake")`), Python

## Development Setup

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
1. Create `.streamlit/secrets.toml` with Snowflake credentials:
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

2. **IMPORTANT**: Never commit `.streamlit/secrets.toml` - ensure it's in `.gitignore`

### Running the Application
```bash
# Start the app
streamlit run app.py

# Or with specific port
streamlit run app.py --server.port 8502

# Run in headless mode (no browser)
streamlit run app.py --server.headless true
```

### Testing
See `TESTING_CHECKLIST.md` for comprehensive testing procedures.

Quick test:
```bash
# Verify connection
python scripts/check_schema.py

# Test backup tables exist
python -c "from src.database.snowflake_operations import get_business_units, get_web_names; print('BU:', len(get_business_units()), 'WN:', len(get_web_names()))"
```

## Architecture

### Database Connection
- Use `st.connection("snowflake")` for all database operations
- Connection configuration in `.streamlit/secrets.toml`
- Implement connection pooling and error handling

### Code Organization
- **app.py** - Main Streamlit application entry point
- **database/** - Database connection and query functions
- **utils/** - Validation, formatting, and helper functions
- **components/** - Reusable UI components

### Data Flow
1. User interacts with Streamlit UI
2. Application queries Snowflake via `st.connection()`
3. Data displayed in interactive dataframes
4. User edits trigger validation → parameterized UPDATE queries
5. Success/error feedback to user

### Key Patterns
- Use `st.cache_data` for read-only queries to improve performance
- Always use parameterized queries (never string concatenation) to prevent SQL injection
- Wrap updates in `st.form()` to batch user inputs
- Implement validation before database operations
- Foreign key relationship: `BUSINESS_UNIT_WEB_NAME.BUSINESS_UNIT_ID` → `BUSINESS_UNIT_DETAILS.BUSINESS_UNIT_ID`

### Security Considerations
- Credentials stored only in `secrets.toml`
- Parameterized queries for all database operations
- Input validation on all user-editable fields
- Web name validation: URL-safe characters only (alphanumeric, hyphens, underscores)

## Switching Between Backup and Production

**Current Mode:** BACKUP (safe for development/testing)

**To Switch to Production (ONLY after testing and approval):**
1. Open `config/table_config.py`
2. Change `USE_BACKUP_TABLES = True` to `USE_BACKUP_TABLES = False`
3. Restart the Streamlit application: `streamlit run app.py`
4. Verify mode in header:
   - BACKUP mode: Green "🔒 BACKUP MODE"
   - PRODUCTION mode: Red "⚠️ PRODUCTION MODE"

**CRITICAL:** Test thoroughly on backup tables before switching to production!

## Troubleshooting

**Connection Issues:**
- Verify `.streamlit/secrets.toml` exists and has correct credentials
- Check private key file exists at specified path
- Test connection: Click "Retry Connection" in header

**Data Not Loading:**
- Click "🔄 Refresh" button in sidebar
- Check browser console for errors
- Verify tables exist in Snowflake

**Updates Not Saving:**
- Check validation error messages
- Verify user has UPDATE permissions on tables
- Check logs for detailed error information

**Performance Issues:**
- Cache TTL is 5 minutes - use Refresh to clear
- Large result sets may take longer to load
- Consider adding search filters to reduce data volume
