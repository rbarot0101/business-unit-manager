# Deploying Business Unit Manager to Snowflake Streamlit

## Prerequisites

1. Snowflake account with Streamlit enabled
2. User with CREATE STREAMLIT privilege
3. Access to ODS.PUBLIC schema
4. Backup tables already created (ZZZ_BUSINESS_UNIT_DETAILS_20260417, ZZZ_BUSINESS_UNIT_WEB_NAME_20260417)

## Deployment Steps

### Option 1: Using Snowsight UI (Recommended)

1. **Login to Snowsight**
   - Go to your Snowflake account URL
   - Navigate to Projects → Streamlit

2. **Create New Streamlit App**
   - Click "+ Streamlit App"
   - Name: `BUSINESS_UNIT_MANAGER`
   - Warehouse: `ETL` (or your preferred warehouse)
   - Database: `ODS`
   - Schema: `PUBLIC`

3. **Upload the Code**
   - Copy the entire contents of `streamlit_app.py`
   - Paste into the Snowflake Streamlit editor
   - Click "Run" to test

4. **Configure Permissions**
   - Grant SELECT on backup tables:
     ```sql
     GRANT SELECT ON TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417 TO ROLE YOUR_ROLE;
     GRANT SELECT ON TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_WEB_NAME_20260417 TO ROLE YOUR_ROLE;
     ```
   
   - Grant UPDATE on backup tables:
     ```sql
     GRANT UPDATE ON TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417 TO ROLE YOUR_ROLE;
     GRANT UPDATE ON TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_WEB_NAME_20260417 TO ROLE YOUR_ROLE;
     ```

5. **Test the App**
   - Click "Run" in Snowsight
   - Verify BACKUP mode indicator shows
   - Test viewing data
   - Test selecting a row
   - Test updating a record

6. **Share with Users**
   - Click "Share" button
   - Add users or roles who need access
   - They can access via: Projects → Streamlit → BUSINESS_UNIT_MANAGER

### Option 2: Using SQL Commands

```sql
-- Create Streamlit app from file
CREATE STREAMLIT ODS.PUBLIC.BUSINESS_UNIT_MANAGER
  ROOT_LOCATION = '@ODS.PUBLIC.STREAMLIT_STAGE'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = ETL;

-- Grant permissions
GRANT USAGE ON STREAMLIT ODS.PUBLIC.BUSINESS_UNIT_MANAGER TO ROLE YOUR_ROLE;

-- Grant table permissions
GRANT SELECT, UPDATE ON TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417 TO ROLE YOUR_ROLE;
GRANT SELECT, UPDATE ON TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_WEB_NAME_20260417 TO ROLE YOUR_ROLE;
```

### Option 3: Using Snowflake CLI

```bash
# Upload file to stage
snow stage put streamlit_app.py @ODS.PUBLIC.STREAMLIT_STAGE --overwrite

# Create Streamlit app
snow streamlit create BUSINESS_UNIT_MANAGER \
  --database ODS \
  --schema PUBLIC \
  --warehouse ETL \
  --main-file streamlit_app.py
```

## Configuration

### Switching Between Backup and Production

In `streamlit_app.py`, locate these lines (near the top):

```python
# Configuration - set to True for backup tables, False for production
USE_BACKUP_TABLES = True
BACKUP_DATE = "20260417"
```

**For Testing (Current):**
```python
USE_BACKUP_TABLES = True  # Uses ZZZ_*_20260417 tables
```

**For Production (After approval):**
```python
USE_BACKUP_TABLES = False  # Uses BUSINESS_UNIT_DETAILS and BUSINESS_UNIT_WEB_NAME
```

## Verification Checklist

After deployment, verify:

- [ ] App loads without errors
- [ ] Header shows "🔒 BACKUP MODE" (green)
- [ ] Business Unit Details table loads (310 records)
- [ ] Web Names table loads (310 records with JOIN)
- [ ] Search functionality works
- [ ] Can select a row
- [ ] Edit form appears with data
- [ ] Validation works (try invalid latitude)
- [ ] Update succeeds and shows success message
- [ ] Data refreshes after update
- [ ] Cancel button closes form

## User Access

### Granting Access to Users

```sql
-- Grant access to specific users
GRANT USAGE ON STREAMLIT ODS.PUBLIC.BUSINESS_UNIT_MANAGER TO USER username;

-- Grant access to a role
GRANT USAGE ON STREAMLIT ODS.PUBLIC.BUSINESS_UNIT_MANAGER TO ROLE role_name;

-- Grant table permissions to the role
GRANT SELECT, UPDATE ON TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417 TO ROLE role_name;
GRANT SELECT, UPDATE ON TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_WEB_NAME_20260417 TO ROLE role_name;
```

### Accessing the App

Users can access the app by:
1. Logging into Snowsight
2. Navigate to: **Projects → Streamlit**
3. Click on **BUSINESS_UNIT_MANAGER**

Or direct URL (if shared):
```
https://[your-account].snowflakecomputing.com/streamlit/ODS.PUBLIC.BUSINESS_UNIT_MANAGER
```

## Monitoring

### Check App Logs

In Snowsight:
1. Open the Streamlit app
2. Click the three dots (⋮)
3. Select "Logs"

### Query History

```sql
-- See queries executed by the Streamlit app
SELECT 
    query_text,
    execution_status,
    error_message,
    start_time,
    total_elapsed_time
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE user_name = 'BUSINESS_UNIT_MANAGER'
ORDER BY start_time DESC
LIMIT 100;
```

## Troubleshooting

### App Won't Load
- Check warehouse is running
- Verify user has USAGE privilege on Streamlit app
- Check table permissions

### No Data Showing
- Verify backup tables exist: 
  ```sql
  SHOW TABLES LIKE 'ZZZ_%20260417' IN ODS.PUBLIC;
  ```
- Check table permissions for app role

### Updates Failing
- Verify UPDATE privilege on tables
- Check validation error messages in app
- Review query history for errors

### Performance Issues
- Consider larger warehouse for better performance
- Check if tables need clustering keys
- Review query execution times in history

## Going to Production

**IMPORTANT:** Only after complete testing and approval!

1. **Update Configuration**
   - Edit `streamlit_app.py`
   - Change `USE_BACKUP_TABLES = False`
   - Save and re-upload to Snowflake

2. **Grant Production Table Permissions**
   ```sql
   GRANT SELECT, UPDATE ON TABLE ODS.PUBLIC.BUSINESS_UNIT_DETAILS TO ROLE role_name;
   GRANT SELECT, UPDATE ON TABLE ODS.PUBLIC.BUSINESS_UNIT_WEB_NAME TO ROLE role_name;
   ```

3. **Test First Update**
   - Make a small, non-critical update
   - Verify it succeeded
   - Check production tables directly

4. **Monitor**
   - Watch for errors in first 24 hours
   - Review query history
   - Get user feedback

5. **Keep Backups**
   - Don't drop backup tables for at least 30 days
   - Document any issues encountered

## Support

For issues or questions:
- Check TESTING_CHECKLIST.md for test procedures
- Review CLAUDE.md for architecture details
- Check query history for error details
- Contact: [Your support contact]

## Version History

- v1.0 (2026-04-17): Initial deployment to Snowflake Streamlit
  - Backup mode by default
  - 310 business units, 153 web names
  - Full CRUD operations
  - Comprehensive validation
