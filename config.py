"""Configuration and connection string helpers."""

import os


def get_connection_string() -> str:
    """Get MSSQL connection string from env (full or from parts)."""
    conn = os.getenv("MSSQL_CONNECTION_STRING")
    if conn:
        return conn

    host = os.getenv("MSSQL_HOST", "localhost")
    port = os.getenv("MSSQL_PORT", "1433")
    user = os.getenv("MSSQL_USER", "sa")
    password = os.getenv("MSSQL_PASSWORD", "")
    database = os.getenv("MSSQL_DATABASE", "master")
    driver = "ODBC+Driver+17+for+SQL+Server"

    return (
        f"mssql+pyodbc://{user}:{password}@{host}:{port}/{database}"
        f"?driver={driver}"
    )
