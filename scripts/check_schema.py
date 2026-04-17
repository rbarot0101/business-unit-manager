"""Check the actual schema of backup tables."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.snowflake_config import SnowflakeConfig
import snowflake.connector
from loguru import logger


def check_table_schemas():
    """Check and display the schemas of backup tables."""

    config = SnowflakeConfig.from_streamlit_secrets()
    logger.info(f"Connecting to Snowflake: {config}")

    try:
        conn = snowflake.connector.connect(**config.get_connection_params())
        cursor = conn.cursor()

        # Check BUSINESS_UNIT_DETAILS schema
        print("\n" + "="*80)
        print("BUSINESS_UNIT_DETAILS (Backup) Schema")
        print("="*80)
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM ODS.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'PUBLIC'
                AND TABLE_NAME = 'ZZZ_BUSINESS_UNIT_DETAILS_20260417'
            ORDER BY ORDINAL_POSITION
        """)

        results = cursor.fetchall()
        for row in results:
            print(f"{row[0]:<40} {row[1]:<20} {row[2]}")

        # Check BUSINESS_UNIT_WEB_NAME schema
        print("\n" + "="*80)
        print("BUSINESS_UNIT_WEB_NAME (Backup) Schema")
        print("="*80)
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM ODS.INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'PUBLIC'
                AND TABLE_NAME = 'ZZZ_BUSINESS_UNIT_WEB_NAME_20260417'
            ORDER BY ORDINAL_POSITION
        """)

        results = cursor.fetchall()
        for row in results:
            print(f"{row[0]:<40} {row[1]:<20} {row[2]}")

        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"Failed: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    check_table_schemas()
