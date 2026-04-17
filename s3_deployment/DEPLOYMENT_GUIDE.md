# S3 Deployment - Quick Start Guide

## Step-by-Step Deployment

### 1. Prepare Environment

```bash
# Navigate to s3_deployment directory
cd C:\Users\RB29\Learning\streamlit\business_unit_web_name\s3_deployment

# Install deployment dependencies
pip install boto3 click

# Verify AWS credentials
aws sts get-caller-identity
```

### 2. Review Configuration

Check `metadata.json`:
```bash
# Windows
type metadata.json

# Linux/Mac
cat metadata.json
```

Verify:
- ✅ Snowflake credentials correct
- ✅ Required groups appropriate
- ✅ Version number updated
- ✅ Category and type correct

### 3. Dry Run (Recommended First)

```bash
python deploy_to_s3.py --dry-run
```

This shows what will be uploaded without actually uploading.

### 4. Deploy to Staging

```bash
python deploy_to_s3.py --env staging
```

Expected output:
```
======================================================================
BUSINESS UNIT MANAGER - S3 DEPLOYMENT
======================================================================
Bucket:      s3://com.raymourflanigan.data-apps-hub
Environment: staging
...
✓ Uploaded: app.py -> s3://...
✓ Uploaded: metadata.json -> s3://...
✓ Uploaded: requirements.txt -> s3://...

DEPLOYMENT SUCCESSFUL!
======================================================================
```

### 5. Verify Deployment

```bash
# Option 1: Using script
python deploy_to_s3.py --verify-only --env staging

# Option 2: Using AWS CLI
aws s3 ls s3://com.raymourflanigan.data-apps-hub/staging/forms/data-management/business-unit-manager/
```

### 6. Test in Hub

1. Login to DataApp Hub (staging): `https://your-hub-staging-url`
2. Navigate to: **Forms** → **Data Management**
3. Find: **Business Unit Manager**
4. Click to launch
5. Verify:
   - ✅ App loads without errors
   - ✅ Data displays correctly
   - ✅ Search works
   - ✅ Selection works
   - ✅ Updates work
   - ✅ Backup mode indicator shows

### 7. Deploy to Production (After Testing)

```bash
# Only after staging is verified and approved
python deploy_to_s3.py --env prod
```

## Deployment Scenarios

### Scenario 1: First Time Deployment

```bash
# Staging
python deploy_to_s3.py --env staging

# Test thoroughly in Hub

# Production (after approval)
python deploy_to_s3.py --env prod
```

### Scenario 2: Update Existing App

```bash
# 1. Update version in metadata.json
# Edit: "version": "1.0.1"

# 2. Deploy update
python deploy_to_s3.py --env staging

# 3. Hub will auto-detect changes via ETag
# Users will get updated version on next access
```

### Scenario 3: Different S3 Bucket

```bash
python deploy_to_s3.py \
  --bucket your-custom-bucket \
  --env staging
```

### Scenario 4: Different Category

```bash
python deploy_to_s3.py \
  --category analytics \
  --env staging
```

## Verification Commands

### Check Files in S3

```bash
# List all files
aws s3 ls s3://com.raymourflanigan.data-apps-hub/staging/forms/data-management/business-unit-manager/

# Download and inspect metadata
aws s3 cp s3://com.raymourflanigan.data-apps-hub/staging/forms/data-management/business-unit-manager/metadata.json ./temp_metadata.json
cat temp_metadata.json
```

### Check File Sizes

```bash
aws s3 ls --recursive --human-readable s3://com.raymourflanigan.data-apps-hub/staging/forms/data-management/business-unit-manager/
```

### Test S3 Access

```bash
# Verify you can read/write
aws s3 cp metadata.json s3://com.raymourflanigan.data-apps-hub/test-upload.json
aws s3 rm s3://com.raymourflanigan.data-apps-hub/test-upload.json
```

## Troubleshooting

### Error: "AccessDenied"

**Problem**: No S3 permissions

**Solution**:
```bash
# Check your AWS identity
aws sts get-caller-identity

# Verify bucket access
aws s3 ls s3://com.raymourflanigan.data-apps-hub/

# Contact AWS admin for permissions
```

### Error: "NoSuchBucket"

**Problem**: Bucket doesn't exist or wrong region

**Solution**:
```bash
# List available buckets
aws s3 ls

# Use correct bucket name
python deploy_to_s3.py --bucket correct-bucket-name
```

### Error: "Invalid JSON"

**Problem**: metadata.json syntax error

**Solution**:
```bash
# Validate JSON
python -m json.tool metadata.json

# Fix syntax errors, then redeploy
```

### App Not Showing in Hub

**Check**:
1. Files uploaded correctly? → `aws s3 ls ...`
2. metadata.json valid? → Check JSON syntax
3. User in required_groups? → Check Okta groups
4. Hub restarted? → Wait 5 minutes for cache refresh

## Best Practices

### 1. Version Management

Always increment version before deploying:
```json
{
  "version": "1.0.1"  // Increment from 1.0.0
}
```

### 2. Test in Staging First

```bash
# Always staging first
python deploy_to_s3.py --env staging

# Test thoroughly

# Then production
python deploy_to_s3.py --env prod
```

### 3. Use Dry Run

```bash
# Preview before deploying
python deploy_to_s3.py --dry-run --env prod
```

### 4. Backup Before Updates

```bash
# Download current version
aws s3 cp s3://com.raymourflanigan.data-apps-hub/prod/forms/data-management/business-unit-manager/app.py ./backup/app.py.bak
```

### 5. Document Changes

Update CHANGELOG.md with each deployment:
```markdown
## [1.0.1] - 2026-04-18
- Fixed: Selection sync issue
- Added: Auto-select for single results
- Deployed to: S3 staging
```

## Quick Reference

### Deploy to Staging
```bash
python deploy_to_s3.py
```

### Deploy to Production
```bash
python deploy_to_s3.py --env prod
```

### Dry Run
```bash
python deploy_to_s3.py --dry-run
```

### Verify
```bash
python deploy_to_s3.py --verify-only
```

### Help
```bash
python deploy_to_s3.py --help
```

## Post-Deployment

After successful deployment:

1. **Notify Users**:
   - Announce new app availability
   - Share access instructions
   - Provide user guide link

2. **Monitor**:
   - Check CloudWatch logs for errors
   - Monitor usage metrics
   - Collect user feedback

3. **Document**:
   - Update project documentation
   - Record deployment date/version
   - Note any issues encountered

## Support

**Issues?** Contact:
- **Ram Barot** - Lead Data Engineer
- **Team**: Enterprise & Data Analytics Team

**Documentation**:
- This guide: `DEPLOYMENT_GUIDE.md`
- Full README: `README.md`
- Main project: `../README.md`

---

**Last Updated**: 2026-04-17  
**Version**: 1.0.0
