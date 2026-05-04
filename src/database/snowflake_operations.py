"""Snowflake database operations for business unit management."""

import streamlit as st
import pandas as pd
import snowflake.connector
from typing import Optional, Dict, Any
from loguru import logger
from config.table_config import get_table_names
from src.database.connection_helper import get_connection_params


@st.cache_resource
def get_snowflake_connection():
    """
    Get a cached Snowflake connection using direct connector with RSA key.

    Returns:
        Snowflake connection object
    """
    try:
        params = get_connection_params()
        conn = snowflake.connector.connect(**params)
        logger.info("Snowflake connection established with RSA key authentication")
        return conn
    except Exception as e:
        logger.error(f"Failed to establish Snowflake connection: {e}")
        raise


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_business_units(search_term: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch business unit details. The search term may be a raw STORE_CD,
    a DISPLAY_NAME fragment, or a combined "STORE_CD-DISPLAY_NAME" label.
    When a combined label is provided (contains '-'), only the prefix is used
    to filter on STORE_CD.
    """
    try:
        conn = get_snowflake_connection()
        tables = get_table_names()
        bu_table = f"ODS.PUBLIC.{tables['business_unit_details']}"
        wn_table = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

        base_query = f"SELECT bd.* FROM {bu_table} bd"

        params: Dict[str, Any] = {}
        where_clause = ""

        if search_term:
            # TODO: hyphen-as-combined-label is a heuristic. A DISPLAY_NAME
            # containing "-" (e.g. "Winston-Salem") typed raw would be
            # misrouted as a combined label. Safe today because real
            # DISPLAY_NAME values have no hyphens. Harden by passing an
            # explicit flag from the caller when input came from the picker.
            if "-" in search_term:
                prefix = search_term.split("-", 1)[0]
                where_clause = " WHERE bd.STORE_CD ILIKE %(needle)s"
                params["needle"] = f"%{prefix}%"
            else:
                # Search STORE_CD directly and DISPLAY_NAME via the web-name join
                base_query += (
                    f" LEFT JOIN {wn_table} wn ON bd.STORE_CD = wn.BUSINESS_UNIT_CD"
                )
                where_clause = (
                    " WHERE bd.STORE_CD ILIKE %(needle)s"
                    " OR wn.DISPLAY_NAME ILIKE %(needle)s"
                    " OR wn.BUSINESS_UNIT_CD ILIKE %(needle)s"
                )
                params["needle"] = f"%{search_term}%"

        query = base_query + where_clause + " ORDER BY bd.STORE_CD"

        logger.debug(f"Executing query: {query} params={params}")
        cursor = conn.cursor()
        cursor.execute(query, params)
        df = cursor.fetch_pandas_all()
        logger.info(f"Fetched {len(df)} business unit records from {bu_table}")
        return df

    except Exception as e:
        logger.error(f"Error fetching business units: {e}")
        st.error(f"Failed to fetch business units: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_web_names(search_term: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch web name details with business unit information from configurable tables.

    Args:
        search_term: Optional search term to filter results

    Returns:
        DataFrame containing web name details with business unit info
    """
    try:
        conn = get_snowflake_connection()
        tables = get_table_names()
        bu_table = f"ODS.PUBLIC.{tables['business_unit_details']}"
        wn_table = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

        query = f"""
            SELECT
                bd.STORE_CD,
                wn.BUSINESS_UNIT_CD,
                wn.DISPLAY_NAME,
                wn.ADDRESS_LINE_1,
                wn.ADDRESS_LINE_2,
                wn.CITY,
                wn.STATE,
                wn.POSTAL_CODE
            FROM {bu_table} bd
            LEFT JOIN {wn_table} wn
                ON bd.STORE_CD = wn.BUSINESS_UNIT_CD
        """

        if search_term:
            query += f" WHERE wn.DISPLAY_NAME ILIKE '%{search_term}%' OR wn.CITY ILIKE '%{search_term}%' OR CAST(wn.BUSINESS_UNIT_CD AS VARCHAR) LIKE '%{search_term}%'"

        query += " ORDER BY bd.STORE_CD"

        logger.debug(f"Executing query: {query}")
        cursor = conn.cursor()
        cursor.execute(query)
        df = cursor.fetch_pandas_all()
        logger.info(f"Fetched {len(df)} web name records from {wn_table}")
        return df

    except Exception as e:
        logger.error(f"Error fetching web names: {e}")
        st.error(f"Failed to fetch web names: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_store_labels() -> pd.DataFrame:
    """
    Fetch the join of business unit details and web names, producing one row
    per store with columns BUSINESS_UNIT_CD, DISPLAY_NAME, and COMBINED_LABEL
    ("BUSINESS_UNIT_CD-DISPLAY_NAME"). Used to resolve sidebar search terms
    into a canonical store label.

    Returns:
        DataFrame with columns: BUSINESS_UNIT_CD, DISPLAY_NAME, COMBINED_LABEL
    """
    try:
        conn = get_snowflake_connection()
        tables = get_table_names()
        bu_table = f"ODS.PUBLIC.{tables['business_unit_details']}"
        wn_table = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

        query = f"""
            SELECT
                wn.BUSINESS_UNIT_CD,
                wn.DISPLAY_NAME,
                wn.BUSINESS_UNIT_CD || '-' || wn.DISPLAY_NAME AS COMBINED_LABEL
            FROM {bu_table} bd
            JOIN {wn_table} wn
                ON bd.STORE_CD = wn.BUSINESS_UNIT_CD
            WHERE wn.BUSINESS_UNIT_CD IS NOT NULL
              AND wn.DISPLAY_NAME IS NOT NULL
            ORDER BY wn.BUSINESS_UNIT_CD
        """

        logger.debug(f"Executing query: {query}")
        cursor = conn.cursor()
        cursor.execute(query)
        df = cursor.fetch_pandas_all()
        logger.info(f"Fetched {len(df)} store labels from {wn_table}")
        return df

    except Exception as e:
        logger.error(f"Error fetching store labels: {e}")
        return pd.DataFrame(columns=["BUSINESS_UNIT_CD", "DISPLAY_NAME", "COMBINED_LABEL"])


def update_business_unit(store_cd: str, updates: Dict[str, Any]) -> bool:
    """
    Update a business unit record in configurable table (backup or production).

    Args:
        store_cd: Store code of the business unit to update
        updates: Dictionary of column names and new values

    Returns:
        True if update successful, False otherwise
    """
    try:
        conn = get_snowflake_connection()
        tables = get_table_names()
        table_name = f"ODS.PUBLIC.{tables['business_unit_details']}"

        # Build SET clause
        set_clause = ", ".join([f"{col} = :{col}" for col in updates.keys()])

        query = f"""
            UPDATE {table_name}
            SET {set_clause}
            WHERE STORE_CD = :store_cd
        """

        params = {**updates, 'store_cd': store_cd}

        logger.debug(f"Executing update query: {query} with params: {params}")

        # Execute update
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

        logger.info(f"Successfully updated business unit {store_cd} in {table_name}")

        # Clear cache to reflect changes
        get_business_units.clear()
        get_web_names.clear()

        return True

    except Exception as e:
        logger.error(f"Error updating business unit {store_cd}: {e}")
        st.error(f"Failed to update business unit: {str(e)}")
        return False


def update_web_name(business_unit_cd: str, updates: Dict[str, Any]) -> bool:
    """
    Update a web name record in configurable table (backup or production).

    Args:
        business_unit_cd: Code of the business unit
        updates: Dictionary of column names and new values

    Returns:
        True if update successful, False otherwise
    """
    try:
        conn = get_snowflake_connection()
        tables = get_table_names()
        table_name = f"ODS.PUBLIC.{tables['business_unit_web_name']}"

        # Build SET clause
        set_parts = []
        params = {'business_unit_cd': business_unit_cd}

        for col, val in updates.items():
            set_parts.append(f"{col} = :{col}")
            params[col] = val

        set_clause = ", ".join(set_parts)

        query = f"""
            UPDATE {table_name}
            SET {set_clause}
            WHERE BUSINESS_UNIT_CD = :business_unit_cd
        """

        logger.debug(f"Executing update query: {query} with params: {params}")

        # Execute update
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

        logger.info(f"Successfully updated web name for business unit {business_unit_cd} in {table_name}")

        # Clear cache to reflect changes
        get_business_units.clear()
        get_web_names.clear()

        return True

    except Exception as e:
        logger.error(f"Error updating web name for business unit {business_unit_cd}: {e}")
        st.error(f"Failed to update web name: {str(e)}")
        return False
