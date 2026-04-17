# S3 Deployment Summary

## What Was Created

A complete S3-compatible deployment package for the Business Unit Manager to run in the EDA Data Apps Hub.

### Files Created

```
s3_deployment/
├── app.py                    ✅ S3-compatible application
├── metadata.json             ✅ Hub configuration
├── requirements.txt          ✅ Dependencies list
├── deploy_to_s3.py          ✅ Deployment automation
├── README.md                 ✅ Complete documentation
├── DEPLOYMENT_GUIDE.md       ✅ Step-by-step guide
└── S3_DEPLOYMENT_SUMMARY.md  ✅ This file
```

## Key Differences from Snowflake Version

### Connection Management
**Snowflake Version** (`streamlit_app.py`):
```python
from snowflake.snowpark.context import get_active_session
session = get_active_session()
```

**S3 Version** (`s3_deployment/app.py`):
```python
# Connection injected by Hub via session state
conn = st.session_state["snowflake_connection"]
```

### Entry Point
- **Snowflake**: Executed directly in Snowflake Streamlit environment
- **S3**: Dynamically loaded by Hub's S3 app loader

### Configuration
- **Snowflake**: Uses Snowflake's built-in auth
- **S3**: Uses credentials from `metadata.json` + AWS Secrets Manager

## Deployment Options Comparison

| Feature | Local Dev | Snowflake Streamlit | S3/DataApp Hub |
|---------|-----------|---------------------|----------------|
| **File** | `app.py` | `streamlit_app.py` | `s3_deployment/app.py` |
| **Connection** | External | Native Session | Hub Injected |
| **Auth** | secrets.toml | Snowflake Auth | Okta + metadata.json |
| **Discovery** | Manual | Snowsight UI | Auto-discovery |
| **Access Control** | None | Snowflake Roles | Okta Groups |
| **Updates** | Manual | Redeploy | Auto via ETag |
| **Multi-App** | Single | Single | Hub aggregates many |

## How S3 Deployment Works

### 1. Upload to S3
```bash
python deploy_to_s3.py --env staging
```

Uploads to:
```
s3://com.raymourflanigan.data-apps-hub/staging/forms/data-management/business-unit-manager/
├── app.py
├── metadata.json
└── requirements.txt
```

### 2. Hub Discovery
- Hub scans S3 on startup
- Finds all apps matching pattern
- Parses `metadata.json` for each app
- Builds navigation dynamically

### 3. User Access
- User logs in via Okta
- Hub checks user's groups against `required_groups` in metadata
- Only shows apps user has access to

### 4. App Execution
When user clicks app:
1. Hub downloads files from S3 to local cache
2. Uses ETag for cache invalidation
3. Injects Snowflake connection from metadata.json config
4. Executes app in isolated Python context
5. Renders within Hub's UI framework

### 5. Auto-Updates
- Hub checks ETags on each access
- Downloads new version if changed
- No manual refresh needed
- Users always get latest version

## Metadata Configuration

The `metadata.json` drives Hub integration:

```json
{
  "name": "Business Unit Manager",          // Display name
  "identifier": "business-unit-manager",    // Unique ID
  "type": "form",                           // App type (form/insight/agent)
  "category": "data-management",            // Navigation category
  "required_groups": ["data_team", "admin"],// Okta groups
  "snowflake_config": {                     // DB credentials
    "account": "re18978.us-east-1",
    "user": "BI_SYS_USR",
    "warehouse": "ETL",
    ...
  }
}
```

## Access Control

### Okta Groups
Users must belong to at least one group:
- `data_team` - Data engineers and analysts
- `admin` - System administrators

### Snowflake Permissions
The `BI_SYS_USR` needs:
- SELECT on backup/production tables
- UPDATE on backup/production tables
- USAGE on ETL warehouse

## Deployment Workflow

### First Time Deployment

```bash
# 1. Navigate to deployment folder
cd s3_deployment

# 2. Review configuration
cat metadata.json

# 3. Preview deployment
python deploy_to_s3.py --dry-run

# 4. Deploy to staging
python deploy_to_s3.py --env staging

# 5. Verify upload
python deploy_to_s3.py --verify-only --env staging

# 6. Test in Hub (staging)
# Navigate to Hub → Forms → Data Management → Business Unit Manager

# 7. Deploy to production (after approval)
python deploy_to_s3.py --env prod
```

### Update Deployment

```bash
# 1. Update version in metadata.json
# "version": "1.0.1"

# 2. Deploy update
python deploy_to_s3.py --env staging

# 3. Hub auto-detects changes
# Users get new version on next access
```

## Testing Checklist

Before deploying to production:

**S3 Upload**
- [ ] All files uploaded successfully
- [ ] Files visible in S3 bucket
- [ ] metadata.json valid JSON
- [ ] Version number incremented

**Hub Integration**
- [ ] App appears in navigation
- [ ] Correct category (Data Management)
- [ ] Correct icon (🏢)
- [ ] Access restricted to required groups

**Functionality**
- [ ] App loads without errors
- [ ] Snowflake connection works
- [ ] Data displays correctly
- [ ] Search functions
- [ ] Selection works
- [ ] Updates succeed
- [ ] Backup mode indicator shows

**Security**
- [ ] Only authorized users can access
- [ ] Snowflake credentials secure
- [ ] No sensitive data in logs

## Troubleshooting

### App Not Appearing

**Check**:
1. Files in S3? → `aws s3 ls s3://bucket/path`
2. Valid metadata.json? → `python -m json.tool metadata.json`
3. User in required groups? → Check Okta
4. Hub restarted? → Wait 5 min for cache

### Connection Errors

**Check**:
1. Snowflake credentials in metadata.json
2. Private key in Secrets Manager
3. User has table permissions
4. Warehouse is running

### Cache Issues

**Solution**:
- Hub uses ETag-based caching
- Changes auto-detected
- Force refresh: restart Hub or wait for cache TTL (5 min)

## Benefits of S3 Deployment

### For Users
✅ Single portal for all apps  
✅ Unified Okta authentication  
✅ Consistent navigation  
✅ No app switching  
✅ Auto-updates  

### For Developers
✅ Independent deployment  
✅ No Hub code changes  
✅ Version control  
✅ Easy rollback  
✅ A/B testing possible  

### For Operations
✅ Centralized management  
✅ Automated discovery  
✅ Group-based access  
✅ CloudWatch metrics  
✅ Audit logging  

## Migration Path

### From Snowflake Streamlit to S3

1. ✅ **Already done**: Created S3-compatible version
2. Deploy to S3 staging
3. Test both versions in parallel
4. Train users on Hub navigation
5. Migrate users to Hub version
6. Optional: Deprecate Snowflake version

### Coexistence
Both versions can run simultaneously:
- **Snowflake Streamlit**: Direct Snowflake users
- **S3/Hub**: Portal users via Hub

## Next Steps

### Immediate
1. Deploy to staging
2. Test with pilot users
3. Gather feedback
4. Fix any issues

### Short Term
1. Deploy to production
2. Announce to data team
3. Create training materials
4. Monitor usage metrics

### Future Enhancements
1. Add more features to metadata
2. Create multiple category variations
3. Develop related apps
4. Build app suite in Hub

## Support Resources

**Documentation**:
- `README.md` - Full S3 deployment docs
- `DEPLOYMENT_GUIDE.md` - Step-by-step guide
- Main `../README.md` - Overall project docs

**Key Commands**:
```bash
# Deploy to staging
python deploy_to_s3.py

# Deploy to production  
python deploy_to_s3.py --env prod

# Verify deployment
python deploy_to_s3.py --verify-only

# Preview deployment
python deploy_to_s3.py --dry-run

# Get help
python deploy_to_s3.py --help
```

**Contact**:
- **Ram Barot** - Lead Data Engineer
- **Team**: Enterprise & Data Analytics Team

## Summary

✅ **Complete S3 deployment package created**  
✅ **Hub-compatible app version**  
✅ **Automated deployment script**  
✅ **Comprehensive documentation**  
✅ **Ready for staging deployment**  

The Business Unit Manager can now be deployed to S3 and dynamically loaded by the EDA Data Apps Hub, providing users with a unified portal experience while maintaining all existing functionality.

---

**Created**: 2026-04-17  
**Version**: 1.0.0  
**Status**: Ready for Deployment
