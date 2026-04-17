"""Snowflake connection configuration."""

from dataclasses import dataclass
import os
from typing import Optional
from pathlib import Path
import tomli
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


@dataclass
class SnowflakeConfig:
    """Configuration for Snowflake database connection."""

    account: str
    user: str
    database: str
    schema: str
    warehouse: str
    role: str
    password: Optional[str] = None
    private_key_file: Optional[str] = None
    _private_key_bytes: Optional[bytes] = None

    @classmethod
    def from_streamlit_secrets(cls) -> 'SnowflakeConfig':
        """
        Load Snowflake configuration from .streamlit/secrets.toml

        Returns:
            SnowflakeConfig: Configuration object with RSA key auth

        Raises:
            FileNotFoundError: If secrets.toml not found
            ValueError: If required fields missing
        """
        secrets_path = Path('.streamlit/secrets.toml')

        if not secrets_path.exists():
            raise FileNotFoundError(
                f"Secrets file not found at {secrets_path}. "
                "Please ensure .streamlit/secrets.toml exists."
            )

        with open(secrets_path, 'rb') as f:
            secrets = tomli.load(f)

        sf_config = secrets.get('connections', {}).get('snowflake', {})

        if not sf_config:
            raise ValueError("Snowflake connection config not found in secrets.toml")

        return cls(
            account=sf_config['account'],
            user=sf_config['user'],
            database=sf_config['database'],
            schema=sf_config['schema'],
            warehouse=sf_config['warehouse'],
            role=sf_config['role'],
            private_key_file=sf_config.get('private_key_path') or sf_config.get('private_key_file')
        )

    def get_private_key_bytes(self) -> Optional[bytes]:
        """
        Load and return private key bytes from file.

        Returns:
            Private key bytes in DER format
        """
        if self._private_key_bytes:
            return self._private_key_bytes

        if not self.private_key_file:
            return None

        key_path = Path(self.private_key_file)
        if not key_path.exists():
            raise FileNotFoundError(f"Private key file not found: {key_path}")

        with open(key_path, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,  # No password on the key file
                backend=default_backend()
            )

        self._private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        return self._private_key_bytes

    def get_connection_params(self) -> dict:
        """
        Get connection parameters as a dictionary for snowflake.connector.

        Returns:
            dict: Connection parameters (with RSA key if configured)
        """
        params = {
            'account': self.account,
            'user': self.user,
            'database': self.database,
            'schema': self.schema,
            'warehouse': self.warehouse,
            'role': self.role
        }

        # Use RSA key authentication if available
        if self.private_key_file:
            params['private_key'] = self.get_private_key_bytes()
        elif self.password:
            params['password'] = self.password
        else:
            raise ValueError(
                "No authentication method configured. "
                "Provide either private_key_file or password."
            )

        return params

    def __repr__(self) -> str:
        """String representation with masked password."""
        return (
            f"SnowflakeConfig(account='{self.account}', user='{self.user}', "
            f"database='{self.database}', schema='{self.schema}', "
            f"warehouse='{self.warehouse}', role='{self.role}')"
        )
