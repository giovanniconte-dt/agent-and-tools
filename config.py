"""
Configurazione per Agent SQL

Gestisce la connessione SQL Server allo stesso modo di ticket-classifier.
Usa ODBC Driver 17 for SQL Server.
"""

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

# Configurazione SQL Server (come ticket-classifier)
SQL_SERVER_CONFIG = {
    "driver": os.getenv("SQL_SERVER_DRIVER", "ODBC Driver 17 for SQL Server"),
    "server": os.getenv("SQL_SERVER", ""),
    "database": os.getenv("SQL_DATABASE", ""),
    "username": os.getenv("SQL_USERNAME", ""),
    "password": os.getenv("SQL_PASSWORD", ""),
    "trusted_connection": os.getenv("SQL_TRUSTED_CONNECTION", "no").lower() == "yes",
}


def get_connection_string() -> str:
    """
    Costruisce la connection string per SQL Server (SQLAlchemy format).

    Supporta:
    - MSSQL_CONNECTION_STRING: override con URL completo (per compatibilità)
    - SQL_SERVER_*: come ticket-classifier (driver, server, database, username, password, trusted_connection)

    Returns:
        Connection string per SQLAlchemy (mssql+pyodbc)
    """
    conn = os.getenv("MSSQL_CONNECTION_STRING")
    if conn:
        return conn

    config = SQL_SERVER_CONFIG
    driver = config["driver"].replace(" ", "+")
    server = config["server"]
    database = config["database"]

    if not server or not database:
        raise ValueError(
            "SQL_SERVER e SQL_DATABASE devono essere impostati. "
            "Copia .env.example in .env e configura le variabili."
        )

    # Parsing server (può essere "host" o "host,port")
    if "," in server:
        host, port = server.split(",", 1)
        host = host.strip()
        port = port.strip()
    else:
        host = server.strip()
        port = os.getenv("SQL_PORT", "1433")

    if config["trusted_connection"]:
        # Windows Authentication (Trusted Connection)
        params = f"driver={driver}&Trusted_Connection=yes"
        return f"mssql+pyodbc://@{host}:{port}/{database}?{params}"
    else:
        # SQL Server Authentication
        username = config["username"]
        password = config["password"]
        if not username or not password:
            raise ValueError(
                "SQL_USERNAME e SQL_PASSWORD devono essere impostati per SQL Server Authentication. "
                "Oppure usa SQL_TRUSTED_CONNECTION=yes per Windows Authentication."
            )
        user_enc = quote_plus(username)
        pass_enc = quote_plus(password)
        params = f"driver={driver}"
        return f"mssql+pyodbc://{user_enc}:{pass_enc}@{host}:{port}/{database}?{params}"
