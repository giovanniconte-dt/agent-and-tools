"""SQL tools for read and write operations on the database."""

from langchain.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine


def create_sql_tools(connection_string: str) -> list:
    """
    Create read_sql and write_sql tools bound to the given database.

    Args:
        connection_string: SQLAlchemy connection string for Microsoft SQL Server.
            Example: mssql+pyodbc://user:pass@host:1433/db?driver=ODBC+Driver+17+for+SQL+Server

    Returns:
        List of [read_sql, write_sql] tools.
    """
    engine = create_engine(connection_string)
    db = SQLDatabase(engine)

    @tool
    def read_sql(query: str) -> str:
        """Execute a SELECT query on the database. Use this for reading data.
        Input must be a valid SQL SELECT statement only. Returns query results as text."""
        q = query.strip().upper()
        if not q.startswith("SELECT"):
            return "Error: read_sql accepts only SELECT queries. Use write_sql for INSERT, UPDATE, DELETE."
        try:
            return db.run(query)
        except Exception as e:
            return f"Error executing query: {e}"

    @tool
    def write_sql(query: str) -> str:
        """Execute an UPDATE query on the database. Use this for modifying data.
        Input must be a valid SQL UPDATE statement only. Returns execution result."""
        q = query.strip().upper()
        allowed = ("UPDATE")
        if not any(q.startswith(kw) for kw in allowed):
            return "Error: write_sql accepts only UPDATE queries. Use read_sql for SELECT."
        try:
            return db.run(query)
        except Exception as e:
            return f"Error executing query: {e}"

    return [read_sql, write_sql]
