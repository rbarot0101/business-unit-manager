"""Helper functions for Snowflake connection with RSA key authentication."""

import streamlit as st
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from loguru import logger


def load_private_key_bytes(key_file_path: str) -> bytes:
    """
    Load private key from file and return as bytes in DER format.

    Args:
        key_file_path: Path to the .p8 private key file

    Returns:
        bytes: Private key in DER format for Snowflake authentication
    """
    key_path = Path(key_file_path)

    if not key_path.exists():
        raise FileNotFoundError(f"Private key file not found: {key_path}")

    with open(key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    return private_key_bytes


def get_connection_params() -> dict:
    """
    Get Snowflake connection parameters from secrets with private key loaded.

    Returns:
        dict: Connection parameters ready for snowflake.connector.connect()
    """
    # Get secrets
    secrets = st.secrets["connections"]["snowflake"]

    # Load private key if specified
    private_key_bytes = None
    if "private_key_file" in secrets:
        private_key_bytes = load_private_key_bytes(secrets["private_key_file"])
        logger.info(f"Loaded private key from {secrets['private_key_file']}")

    # Build connection params
    params = {
        "account": secrets["account"],
        "user": secrets["user"],
        "warehouse": secrets["warehouse"],
        "database": secrets["database"],
        "schema": secrets["schema"],
        "role": secrets["role"]
    }

    # Add authentication
    if private_key_bytes:
        params["private_key"] = private_key_bytes
    elif "password" in secrets:
        params["password"] = secrets["password"]
    else:
        raise ValueError("No authentication method found in secrets (private_key_file or password required)")

    return params
