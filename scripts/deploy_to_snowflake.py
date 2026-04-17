"""Deploy Business Unit Manager to Snowflake Streamlit."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.snowflake_config import SnowflakeConfig
import snowflake.connector
from loguru import logger


def deploy_streamlit_app():
    """Deploy the Streamlit app to Snowflake."""

    config = SnowflakeConfig.from_streamlit_secrets()
    logger.info(f"Connecting to Snowflake: {config}")

    try:
        conn = snowflake.connector.connect(**config.get_connection_params())
        cursor = conn.cursor()

        print("\n" + "="*70)
        print("DEPLOYING BUSINESS UNIT MANAGER TO SNOWFLAKE STREAMLIT")
        print("="*70)

        # Step 1: Create stage if it doesn't exist
        logger.info("Step 1: Creating stage for Streamlit files...")
        cursor.execute("""
            CREATE STAGE IF NOT EXISTS ODS.PUBLIC.STREAMLIT_STAGE
            COMMENT = 'Stage for Streamlit application files'
        """)
        print("[OK] Stage created/verified: ODS.PUBLIC.STREAMLIT_STAGE")

        # Step 2: Upload streamlit_app.py to stage
        logger.info("Step 2: Uploading streamlit_app.py to stage...")
        app_file = Path(__file__).parent.parent / "streamlit_app.py"

        cursor.execute(f"""
            PUT file://{str(app_file).replace(chr(92), '/')}
            @ODS.PUBLIC.STREAMLIT_STAGE
            AUTO_COMPRESS=FALSE
            OVERWRITE=TRUE
        """)
        print("[OK] Uploaded streamlit_app.py to stage")

        # Step 3: Create or replace Streamlit app
        logger.info("Step 3: Creating Streamlit app...")
        cursor.execute("""
            CREATE OR REPLACE STREAMLIT ODS.PUBLIC.BUSINESS_UNIT_MANAGER
            ROOT_LOCATION = '@ODS.PUBLIC.STREAMLIT_STAGE'
            MAIN_FILE = 'streamlit_app.py'
            QUERY_WAREHOUSE = ETL
            COMMENT = 'Business Unit Manager - Manage business unit data with backup-first approach'
        """)
        print("[OK] Created Streamlit app: ODS.PUBLIC.BUSINESS_UNIT_MANAGER")

        # Step 4: Grant permissions on Streamlit app
        logger.info("Step 4: Granting permissions...")
        try:
            cursor.execute("""
                GRANT USAGE ON STREAMLIT ODS.PUBLIC.BUSINESS_UNIT_MANAGER TO ROLE SYSADMIN
            """)
            print("[OK] Granted USAGE on Streamlit app to SYSADMIN")
        except Exception as e:
            print(f"[WARN] Could not grant to SYSADMIN (may not be needed): {e}")

        # Step 5: Verify table permissions exist
        logger.info("Step 5: Verifying table permissions...")

        # Check if backup tables are accessible
        cursor.execute("""
            SELECT COUNT(*)
            FROM ODS.PUBLIC.ZZZ_BUSINESS_UNIT_DETAILS_20260417
        """)
        bu_count = cursor.fetchone()[0]
        print(f"[OK] Can access ZZZ_BUSINESS_UNIT_DETAILS_20260417: {bu_count} rows")

        cursor.execute("""
            SELECT COUNT(*)
            FROM ODS.PUBLIC.ZZZ_BUSINESS_UNIT_WEB_NAME_20260417
        """)
        wn_count = cursor.fetchone()[0]
        print(f"[OK] Can access ZZZ_BUSINESS_UNIT_WEB_NAME_20260417: {wn_count} rows")

        # Step 6: Get app URL
        cursor.execute("""
            SHOW STREAMLITS LIKE 'BUSINESS_UNIT_MANAGER' IN ODS.PUBLIC
        """)
        result = cursor.fetchone()

        print("\n" + "="*70)
        print("DEPLOYMENT SUCCESSFUL!")
        print("="*70)
        print(f"App Name: BUSINESS_UNIT_MANAGER")
        print(f"Database: ODS.PUBLIC")
        print(f"Warehouse: ETL")
        print(f"Status: Ready for use")
        print(f"\nBackup Tables Connected:")
        print(f"  - Business Units: {bu_count} records")
        print(f"  - Web Names: {wn_count} records")
        print("\nAccess Instructions:")
        print("  1. Log into Snowsight")
        print("  2. Navigate to: Projects → Streamlit")
        print("  3. Click on: BUSINESS_UNIT_MANAGER")
        print("\nOr share with users:")
        print("  Click 'Share' in Snowsight to grant access to specific users/roles")
        print("\n[IMPORTANT] App is in BACKUP mode (safe for testing)")
        print("  - All changes affect ZZZ_*_20260417 tables only")
        print("  - Production tables remain untouched")
        print("="*70)

        return True

    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        print(f"\n[ERROR] Deployment failed: {e}")
        print("\nTroubleshooting:")
        print("  - Verify you have CREATE STREAMLIT privilege")
        print("  - Check warehouse ETL is available")
        print("  - Verify table access permissions")
        return False
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    success = deploy_streamlit_app()
    sys.exit(0 if success else 1)
