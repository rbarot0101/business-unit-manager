"""Create backup tables in Snowflake for safe development."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.snowflake_config import SnowflakeConfig
import snowflake.connector
from loguru import logger


def create_backup_tables():
    """Create backup tables in Snowflake."""

    # Load configuration
    config = SnowflakeConfig.from_streamlit_secrets()
    logger.info(f"Connecting to Snowflake: {config}")

    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(**config.get_connection_params())
        cursor = conn.cursor()

        logger.info("Connected to Snowflake successfully")

        # Create backup of BUSINESS_UNIT_DETAILS
        logger.info("Creating backup of BUSINESS_UNIT_DETAILS...")
        cursor.execute("""
            CREATE TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417 AS
            SELECT * FROM ODS.PUBLIC.BUSINESS_UNIT_DETAILS
        """)
        logger.success("✓ Created ZZZ_BUSINESS_UNIT_DETAILS_20260417")

        # Create backup of BUSINESS_UNIT_WEB_NAME
        logger.info("Creating backup of BUSINESS_UNIT_WEB_NAME...")
        cursor.execute("""
            CREATE TABLE ODS.PUBLIC.ZZZ_BUSINESS_UNIT_WEB_NAME_20260417 AS
            SELECT * FROM ODS.PUBLIC.BUSINESS_UNIT_WEB_NAME
        """)
        logger.success("✓ Created ZZZ_BUSINESS_UNIT_WEB_NAME_20260417")

        # Verify row counts
        logger.info("\nVerifying row counts...")
        cursor.execute("""
            SELECT
                'BUSINESS_UNIT_DETAILS (PROD)' AS TABLE_NAME,
                COUNT(*) AS ROW_COUNT
            FROM ODS.PUBLIC.BUSINESS_UNIT_DETAILS
            UNION ALL
            SELECT
                'ZZZ_BUSINESS_UNIT_DETAILS_20260417 (BACKUP)',
                COUNT(*)
            FROM ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417
            UNION ALL
            SELECT
                'BUSINESS_UNIT_WEB_NAME (PROD)',
                COUNT(*)
            FROM ODS.PUBLIC.BUSINESS_UNIT_WEB_NAME
            UNION ALL
            SELECT
                'ZZZ_BUSINESS_UNIT_WEB_NAME_20260417 (BACKUP)',
                COUNT(*)
            FROM ODS.PUBLIC.ZZZ_BUSINESS_UNIT_WEB_NAME_20260417
        """)

        results = cursor.fetchall()

        print("\n" + "="*60)
        print("BACKUP VERIFICATION")
        print("="*60)
        for row in results:
            print(f"{row[0]:<50} {row[1]:>8}")
        print("="*60)

        # Verify counts match
        prod_bu = results[0][1]
        backup_bu = results[1][1]
        prod_wn = results[2][1]
        backup_wn = results[3][1]

        if prod_bu == backup_bu and prod_wn == backup_wn:
            logger.success("\n✓ All backup row counts match production!")
            logger.success("✓ Safe to proceed with development")
            return True
        else:
            logger.error("\n✗ Row count mismatch detected!")
            logger.error("✗ DO NOT proceed - investigate the issue")
            return False

    except Exception as e:
        logger.error(f"Failed to create backups: {e}")
        return False
    finally:
        if conn:
            conn.close()
            logger.info("Connection closed")


if __name__ == "__main__":
    success = create_backup_tables()
    sys.exit(0 if success else 1)
