"""Table configuration for development vs production environment.

This module provides a toggle between backup tables (for safe development)
and production tables (for live deployment).

IMPORTANT: Always develop and test on backup tables first!
"""

# CONFIGURATION
# Set to True for development (uses backup tables)
# Set to False for production (uses live tables)
USE_BACKUP_TABLES = True

# Backup date identifier
BACKUP_DATE = "20260417"


def get_table_names() -> dict:
    """
    Get table names based on environment setting.

    Returns:
        dict: Dictionary with keys 'business_unit_details' and 'business_unit_web_name'
              containing the appropriate table names for the current environment.

    Examples:
        >>> # In development mode (USE_BACKUP_TABLES = True)
        >>> get_table_names()
        {
            'business_unit_details': 'ZZZ_BUSINESS_UNIT_DETAILS_20260417',
            'business_unit_web_name': 'ZZZ_BUSINESS_UNIT_WEB_NAME_20260417'
        }

        >>> # In production mode (USE_BACKUP_TABLES = False)
        >>> get_table_names()
        {
            'business_unit_details': 'BUSINESS_UNIT_DETAILS',
            'business_unit_web_name': 'BUSINESS_UNIT_WEB_NAME'
        }
    """
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


def get_environment_mode() -> str:
    """
    Get current environment mode as a string.

    Returns:
        str: Either 'BACKUP' or 'PRODUCTION'
    """
    return 'BACKUP' if USE_BACKUP_TABLES else 'PRODUCTION'


def is_backup_mode() -> bool:
    """
    Check if currently in backup mode.

    Returns:
        bool: True if using backup tables, False if using production tables
    """
    return USE_BACKUP_TABLES
