"""Schema tools for listing tables and getting table structure."""

from langchain.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine


def create_schema_tools(connection_string: str) -> list:
    """
    Create list_tables and get_table_structure tools bound to the given database.

    Args:
        connection_string: SQLAlchemy connection string for Microsoft SQL Server.

    Returns:
        List of [list_tables, get_table_structure] tools.
    """
    engine = create_engine(connection_string)
    db = SQLDatabase(engine)

    @tool
    def list_tables() -> str:
        """List all table names in the database. Use this to discover available tables."""
        try:
            tables = list(db.get_usable_table_names())
            if not tables:
                return "No tables found in the database."
            return "Tables: " + ", ".join(tables)
        except Exception as e:
            return f"Error listing tables: {e}"

    @tool
    def get_table_structure(table_names: str) -> str:
        """Get the schema/structure of one or more tables. Input: comma-separated table names.
        Example: 'users' or 'users, orders'"""
        try:
            names = [n.strip() for n in table_names.split(",") if n.strip()]
            if not names:
                return "Error: provide at least one table name (comma-separated for multiple)."
            return db.get_table_info(table_names=names)
        except Exception as e:
            return f"Error getting table structure: {e}"

    return [list_tables, get_table_structure]
