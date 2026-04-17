# Scripts Documentation

## Backup Creation

### create_backups.py

Creates backup tables in Snowflake for safe development and testing.

**Usage:**
```bash
python scripts/create_backups.py
```

**What it does:**
1. Connects to Snowflake using credentials from `.streamlit/secrets.toml`
2. Creates `ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417` as a copy of production table
3. Creates `ODS.PUBLIC.ZZZ_BUSINESS_UNIT_WEB_NAME_20260417` as a copy of production table
4. Verifies row counts match between production and backup tables
5. Reports success or failure

**Prerequisites:**
- `.streamlit/secrets.toml` must be configured with valid Snowflake credentials
- User must have CREATE TABLE permissions in ODS.PUBLIC schema
- User must have SELECT permissions on production tables

**Expected Output:**
```
============================================================
BACKUP VERIFICATION
============================================================
BUSINESS_UNIT_DETAILS (PROD)                          1234
ZZZ_BUSINESS_UNIT_DETAILS_20260417 (BACKUP)           1234
BUSINESS_UNIT_WEB_NAME (PROD)                         5678
ZZZ_BUSINESS_UNIT_WEB_NAME_20260417 (BACKUP)          5678
============================================================
✓ All backup row counts match production!
✓ Safe to proceed with development
```

**IMPORTANT:** Do not proceed with development until backups are successfully created and verified.

## SQL Scripts

### create_backup_tables.sql

Contains the raw SQL commands for creating backup tables. Can be executed directly in Snowflake if preferred over the Python script.
