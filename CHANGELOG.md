# Changelog

All notable changes to Business Unit Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-17

**Project Lead:** Ram Barot - Lead Data Engineer, Enterprise & Data Analytics Team

### Added
- Initial production release
- Snowflake Streamlit deployment
- Business Unit Details management (310 records)
- Web Names management (153 records)
- Advanced search functionality with real-time filtering
- Record selection via dropdown interface
- Edit forms with comprehensive validation
- Backup mode for safe testing environment
- Auto-select when search returns single result
- Clear instructions for dropdown-based selection
- Connection monitoring with retry capability
- Mode indicator (Backup/Production) in header
- Session state management for selections
- Automated deployment script
- Comprehensive documentation

### Features
- **Data Viewing**: Interactive tables with 310 business units and 153 web names
- **Search**: Real-time filtering across all columns
- **Edit Capability**: Update latitude, longitude, dates, hours, marketing flags, addresses
- **Validation**: Coordinate ranges, required fields, URL-safe characters
- **Security**: Parameterized queries, input validation, credential management
- **Backup Mode**: Safe testing on ZZZ_*_20260417 tables

### Database
- Created backup tables: ZZZ_BUSINESS_UNIT_DETAILS_20260417 (310 rows)
- Created backup tables: ZZZ_BUSINESS_UNIT_WEB_NAME_20260417 (153 rows)
- Configured production toggle in config/table_config.py

### Documentation
- README.md with quick start guide
- CLAUDE.md for developers
- Deployment guide for Snowflake
- Testing checklist
- Test results documentation
- Product specification
- Implementation plan

### Deployment
- Automated deployment via scripts/deploy_to_snowflake.py
- Snowflake Streamlit app: ODS.PUBLIC.BUSINESS_UNIT_MANAGER
- Stage created: ODS.PUBLIC.STREAMLIT_STAGE
- Permissions configured for SYSADMIN role

### Technical
- Python 3.9+ support
- Streamlit 1.31.0
- Snowflake Snowpark integration
- RSA key authentication (local)
- Session-based authentication (Snowflake)
- Compatibility with older Streamlit version in Snowflake

## [0.5.0] - 2026-04-17

### Fixed
- Auto-select functionality when search returns single result
- Selectbox sync with table switching
- Clear button now resets all selection state
- Search filter properly clears selection when record not in results
- Compatibility with Snowflake's older Streamlit version
- UPDATE query data type handling (numbers, booleans, strings, NULL)
- Removed unsupported parameters (hide_index, selection_mode)
- Changed st.rerun() to st.experimental_rerun() for compatibility

### Changed
- Selection mechanism: dropdown only (table clicks not supported in Snowflake)
- Added visual separator and instructions for record selection
- Improved user guidance with captions and labels
- Table switching now automatically clears selection state

## [0.4.0] - 2026-04-17

### Added
- Snowflake deployment capability
- Two app versions: app.py (local) and streamlit_app.py (Snowflake)
- Deployment success documentation
- Connection testing script

### Changed
- Separated local and Snowflake configurations
- Updated database connection for Snowflake environment
- Modified UI for older Streamlit version compatibility

## [0.3.0] - 2026-04-17

### Added
- Business Unit edit form
- Web Name edit form
- Input validation for all editable fields
- Update handlers with confirmation
- Success/error feedback
- Cache clearing after updates

### Security
- Parameterized SQL queries
- Input validation on coordinates, dates, addresses
- URL-safe character validation for web names

## [0.2.0] - 2026-04-17

### Added
- Data display for both tables
- Search functionality
- Row selection mechanism
- Session state management
- Loading indicators
- Empty state handling

## [0.1.0] - 2026-04-17

### Added
- Project structure
- Snowflake connection configuration
- Table configuration (backup/production toggle)
- Basic Streamlit app skeleton
- Header with mode indicator
- Sidebar navigation
- Database operations module
- Validation utilities
- Deployment scripts
- Initial documentation

### Security
- Credentials in secrets.toml
- .gitignore for sensitive files
- RSA key authentication support

---

## Unreleased

### Planned Features
- Audit logging for all changes
- User role management
- Batch update capability
- Data export functionality (CSV/Excel)
- Advanced filtering options
- Undo/redo for updates
- Email notifications
- Mobile-responsive views
- Automated testing suite
- Performance monitoring
- API endpoints for integration

### Under Consideration
- Multi-user collaboration features
- Change history view
- Scheduled reports
- Data import functionality
- Custom field validation rules
- Approval workflow for updates
- Integration with other systems

---

## Version History Summary

- **v1.0.0** - Production release with full features
- **v0.5.0** - Bug fixes and Snowflake compatibility
- **v0.4.0** - Snowflake deployment
- **v0.3.0** - Edit functionality
- **v0.2.0** - Data display and search
- **v0.1.0** - Initial setup

[1.0.0]: https://github.com/your-org/business-unit-manager/releases/tag/v1.0.0
[0.5.0]: https://github.com/your-org/business-unit-manager/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/your-org/business-unit-manager/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/your-org/business-unit-manager/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/your-org/business-unit-manager/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/your-org/business-unit-manager/releases/tag/v0.1.0
