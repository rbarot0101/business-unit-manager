# Business Unit Manager

A professional Streamlit application for managing business unit data in Snowflake. Provides a secure, user-friendly interface for viewing and updating business unit details and web name information.

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit)](https://snowflake.com)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **📊 Data Viewing**: Browse 310+ business units and 153+ web name records
- **🔍 Advanced Search**: Real-time search across all columns
- **✏️ Edit Capability**: Update records with comprehensive validation
- **🔒 Backup Mode**: Safe testing environment with production protection
- **🚀 Snowflake Native**: Deployed directly in Snowflake Streamlit
- **✅ Data Validation**: Coordinate validation, required fields, input sanitization

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Snowflake account with Streamlit enabled
- Access to ODS.PUBLIC schema
- Required permissions: SELECT, UPDATE on target tables

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd business_unit_web_name
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Snowflake credentials**
   
   Create `.streamlit/secrets.toml`:
   ```toml
   [connections.snowflake]
   account = "your-account"
   user = "your-username"
   password = "your-password"
   warehouse = "ETL"
   database = "ODS"
   schema = "PUBLIC"
   role = "your-role"
   ```

4. **Run locally**
   ```bash
   streamlit run app.py
   ```

### Snowflake Streamlit Deployment

See [deployment/SNOWFLAKE_DEPLOYMENT.md](deployment/SNOWFLAKE_DEPLOYMENT.md) for detailed deployment instructions.

**Quick deploy:**
```bash
python scripts/deploy_to_snowflake.py
```

Access in Snowsight: **Projects → Streamlit → BUSINESS_UNIT_MANAGER**

### S3 Deployment (DataApp Hub)

Deploy to S3 for dynamic loading in EDA Data Apps Hub.

See [s3_deployment/README.md](s3_deployment/README.md) for detailed instructions.

**Quick deploy to staging:**
```bash
cd s3_deployment
python deploy_to_s3.py
```

**Deploy to production:**
```bash
python deploy_to_s3.py --env prod
```

Access in DataApp Hub: **Forms → Data Management → Business Unit Manager**

## Project Structure

```
business_unit_web_name/
├── app.py                      # Local development version
├── streamlit_app.py            # Snowflake production version
├── requirements.txt            # Python dependencies
├── CLAUDE.md                   # Development guidelines
├── README.md                   # This file
│
├── .streamlit/
│   └── secrets.toml           # Snowflake credentials (local only)
│
├── config/
│   ├── snowflake_config.py    # Connection configuration
│   └── table_config.py        # Backup/production toggle
│
├── src/
│   ├── database/
│   │   ├── connection_helper.py
│   │   └── snowflake_operations.py
│   └── utils/
│       └── validators.py      # Input validation functions
│
├── scripts/
│   ├── create_backups.py      # Create backup tables
│   ├── deploy_to_snowflake.py # Automated deployment
│   ├── check_schema.py        # Schema verification
│   └── README.md              # Script documentation
│
├── docs/
│   ├── specs/
│   │   ├── spec.md            # Product specification
│   │   └── implementation_plan.md
│   ├── TESTING_CHECKLIST.md   # QA checklist
│   └── TEST_RESULTS.md        # Test execution results
│
├── deployment/
│   ├── SNOWFLAKE_DEPLOYMENT.md
│   └── DEPLOYMENT_SUCCESS.md
│
├── s3_deployment/             # S3/DataApp Hub deployment
│   ├── app.py                 # S3-compatible app version
│   ├── metadata.json          # Hub app configuration
│   ├── requirements.txt       # Additional dependencies
│   ├── deploy_to_s3.py        # S3 deployment script
│   ├── README.md              # S3 deployment docs
│   └── DEPLOYMENT_GUIDE.md    # Step-by-step guide
│
└── tests/                     # Future: automated tests
```

## Usage

### Viewing Data

1. Select table: **Business Unit Details** or **Web Names**
2. Use search to filter records
3. Browse data in the interactive table

### Editing Records

1. Use the **"Choose a record"** dropdown to select a record
2. Edit form appears with current values
3. Modify fields as needed
4. Click **Update** to save changes
5. Success message confirms the update

### Search Tips

- Search works across all visible columns
- Case-insensitive matching
- Real-time filtering as you type
- When 1 result found, auto-selects that record

## Configuration

### Backup vs Production Mode

Control which tables the app uses via `config/table_config.py`:

```python
USE_BACKUP_TABLES = True   # BACKUP mode (safe for testing)
USE_BACKUP_TABLES = False  # PRODUCTION mode (live data)
```

**Current mode shows in app header:**
- 🔒 Green "BACKUP MODE" - uses ZZZ_*_20260417 tables
- ⚠️ Red "PRODUCTION MODE" - uses live tables

## Security

- ✅ Credentials stored only in secrets.toml (not in code)
- ✅ Parameterized SQL queries (SQL injection prevention)
- ✅ Input validation on all user-editable fields
- ✅ Backup-first development approach
- ✅ secrets.toml excluded from version control

## Data Tables

### Business Unit Details
- **Table**: `ODS.PUBLIC.BUSINESS_UNIT_DETAILS`
- **Backup**: `ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417`
- **Records**: 310
- **Editable Fields**: Latitude, Longitude, Open/Close dates, Store hours, Marketing flag

### Web Names
- **Table**: `ODS.PUBLIC.BUSINESS_UNIT_WEB_NAME`
- **Backup**: `ODS.PUBLIC.ZZZ_BUSINESS_UNIT_WEB_NAME_20260417`
- **Records**: 153
- **Editable Fields**: Display name, Address fields (Line 1/2, City, State, Postal Code)

## Troubleshooting

**Connection Issues**
- Verify secrets.toml has correct credentials
- Check warehouse is running
- Use "Retry Connection" button in app

**Data Not Loading**
- Click "🔄 Refresh" button
- Verify table permissions
- Check logs in Snowsight

**Updates Not Saving**
- Review validation error messages
- Confirm UPDATE permissions
- Check Snowflake query history

See [CLAUDE.md](CLAUDE.md) for complete troubleshooting guide.

## Development

### Running Tests

```bash
# Check schema and connections
python scripts/check_schema.py

# Verify backups exist
python scripts/create_backups.py --verify
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Parameterized queries only (never string concatenation)
- Validate all user inputs
- Clear error messages

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Developer guide and architecture
- **[docs/specs/spec.md](docs/specs/spec.md)** - Product specification
- **[docs/TESTING_CHECKLIST.md](docs/TESTING_CHECKLIST.md)** - QA procedures
- **[deployment/SNOWFLAKE_DEPLOYMENT.md](deployment/SNOWFLAKE_DEPLOYMENT.md)** - Deployment guide
- **[scripts/README.md](scripts/README.md)** - Script documentation

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review query history in Snowflake
3. Check app logs in Snowsight (⋮ → Logs)
4. Consult documentation in docs/

## Version History

**v1.0.0** (2026-04-17)
- Initial production release
- 310 business units, 153 web names
- Backup mode by default
- Full CRUD operations
- Comprehensive validation
- Snowflake Streamlit deployment

## License

MIT License - see LICENSE file for details

## Contributors

**Project Lead:**
- Ram Barot - Lead Data Engineer, Enterprise & Data Analytics Team

**Development:**
- Ram Barot + Claude Code
- Deployment: 2026-04-17
- Environment: Snowflake Streamlit (ODS.PUBLIC)
