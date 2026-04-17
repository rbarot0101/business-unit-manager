# Business Unit Manager - S3 Deployment

Deploy Business Unit Manager to S3 for dynamic loading by the EDA Data Apps Hub.

## Overview

This directory contains the S3-compatible version of the Business Unit Manager application, designed to be dynamically loaded by the DataApp Hub's S3 app loader.

## File Structure

```
s3_deployment/
├── app.py                 # Main application (S3-compatible)
├── metadata.json          # App configuration and metadata
├── requirements.txt       # Additional dependencies (if any)
├── deploy_to_s3.py       # Deployment script
└── README.md             # This file
```

## Prerequisites

1. **AWS CLI configured** with appropriate credentials
2. **S3 bucket** access: `com.raymourflanigan.data-apps-hub`
3. **Python 3.9+** with boto3 and click installed
4. **Permissions**:
   - `s3:PutObject` on target bucket
   - `s3:ListBucket` on target bucket

## Installation

```bash
# Install deployment dependencies
pip install boto3 click
```

## Deployment

### Quick Deploy to Staging

```bash
python deploy_to_s3.py
```

This will upload to:
```
s3://com.raymourflanigan.data-apps-hub/staging/forms/data-management/business-unit-manager/
```

### Deploy to Production

```bash
python deploy_to_s3.py --env prod
```

### Dry Run (Preview without uploading)

```bash
python deploy_to_s3.py --dry-run
```

### Verify Existing Deployment

```bash
python deploy_to_s3.py --verify-only
```

### Custom Deployment

```bash
python deploy_to_s3.py \
  --bucket your-bucket-name \
  --env staging \
  --app-type forms \
  --category data-management \
  --app-name business-unit-manager
```

## S3 Structure

The app will be deployed to:

```
s3://com.raymourflanigan.data-apps-hub/
└── staging/                          # Environment
    └── forms/                        # App type
        └── data-management/          # Category
            └── business-unit-manager/    # App identifier
                ├── app.py
                ├── metadata.json
                └── requirements.txt
```

## Metadata Configuration

The `metadata.json` file contains:

```json
{
  "name": "Business Unit Manager",
  "identifier": "business-unit-manager",
  "description": "Manage business unit details and web names",
  "version": "1.0.0",
  "category": "data-management",
  "type": "form",
  "required_groups": ["data_team", "admin"],
  "snowflake_config": { ... }
}
```

### Key Fields

- **name**: Display name in Hub navigation
- **identifier**: Unique app identifier
- **type**: `form`, `insight`, or `agent`
- **category**: Organizational category
- **required_groups**: Okta groups needed to access
- **snowflake_config**: Database connection settings

## Hub Integration

### Auto-Discovery

The DataApp Hub automatically discovers apps in S3:

1. Scans S3 bucket on startup
2. Parses `metadata.json` for each app
3. Filters by user's Okta groups
4. Builds navigation dynamically

### App Execution

When a user selects the app:

1. Hub downloads app files to cache
2. Injects Snowflake connection via session state
3. Executes `app.py` in isolated context
4. Renders within Hub's UI framework

### Connection Context

The app receives Snowflake connection from Hub:

```python
# Connection is injected by Hub
conn = st.session_state["snowflake_connection"]

# Uses credentials from metadata.json or Hub defaults
```

## Access Control

Users must belong to one of these Okta groups:

- `data_team`
- `admin`

Configure in `metadata.json`:
```json
{
  "required_groups": ["data_team", "admin"]
}
```

## Snowflake Configuration

The app uses these Snowflake credentials (from metadata.json):

```json
{
  "snowflake_config": {
    "account": "re18978.us-east-1",
    "user": "BI_SYS_USR",
    "warehouse": "ETL",
    "database": "ODS",
    "schema": "PUBLIC",
    "role": "SYSADMIN",
    "private_key_path": "staging/snowflake/rsa-private-key/bi_sys_usr"
  }
}
```

## Testing

### Local Testing

Test the S3 version locally before deploying:

```bash
# Set up test environment
export SNOWFLAKE_ACCOUNT="re18978.us-east-1"
export SNOWFLAKE_USER="BI_SYS_USR"
export SNOWFLAKE_WAREHOUSE="ETL"

# Run locally
streamlit run app.py
```

### S3 Testing

After deploying to staging:

1. Login to DataApp Hub (staging)
2. Navigate to: Forms → Data Management
3. Click: Business Unit Manager
4. Verify app loads and functions correctly

## Deployment Checklist

Before deploying:

- [ ] Test app locally
- [ ] Update version in metadata.json
- [ ] Verify Snowflake credentials in metadata.json
- [ ] Check required_groups are correct
- [ ] Run dry-run to preview
- [ ] Deploy to staging first
- [ ] Test in Hub (staging)
- [ ] Get approval for production
- [ ] Deploy to production
- [ ] Verify in Hub (production)

## Troubleshooting

### App Not Appearing in Hub

1. **Check S3 Upload**:
   ```bash
   aws s3 ls s3://com.raymourflanigan.data-apps-hub/staging/forms/data-management/business-unit-manager/
   ```

2. **Verify metadata.json**:
   - Valid JSON syntax
   - Required fields present
   - Identifier matches folder name

3. **Check User Groups**:
   - User belongs to required Okta groups
   - Groups match metadata.json

### Connection Errors

1. **Check Snowflake Credentials**:
   - Account, user, warehouse in metadata.json
   - Private key path correct in Secrets Manager
   - User has permissions on tables

2. **Verify Table Access**:
   ```sql
   -- Test as BI_SYS_USR
   SELECT COUNT(*) FROM ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417;
   ```

### App Crashes

1. **Check Hub Logs**:
   - CloudWatch logs for errors
   - Look for import errors
   - Check for missing dependencies

2. **Verify Dependencies**:
   - All imports available in Hub environment
   - No version conflicts

## Updating the App

To update an existing deployment:

1. **Update Files**:
   ```bash
   # Edit app.py and/or metadata.json
   # Increment version in metadata.json
   ```

2. **Redeploy**:
   ```bash
   python deploy_to_s3.py --env staging
   ```

3. **Hub Auto-Updates**:
   - Hub uses ETag-based caching
   - Will detect changes automatically
   - Downloads updated files on next access

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-17 | Initial S3 deployment |

## Support

**Project Lead**: Ram Barot - Lead Data Engineer  
**Team**: Enterprise & Data Analytics Team

**Resources**:
- Main Project: `../README.md`
- Development Guide: `../CLAUDE.md`
- Hub Documentation: DataApp Hub repository

## Related Documentation

- **Main App**: `../streamlit_app.py` (Snowflake Streamlit version)
- **Local Dev**: `../app.py` (Local development version)
- **Deployment Guide**: `../deployment/SNOWFLAKE_DEPLOYMENT.md`
- **User Guide**: `../docs/USER_GUIDE.md`

---

**Environment:** S3-based Dynamic Loading  
**Hub:** EDA Data Apps Hub  
**Version:** 1.0.0
