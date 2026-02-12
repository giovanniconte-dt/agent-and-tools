"""Create the schema agent with list_tables and get_table_structure tools."""

import os

from langchain.agents import create_agent

from tools.schema_tools import create_schema_tools

SYSTEM_PROMPT = """Sei un assistente che esplora lo schema del database.
Hai accesso a due tool:
- list_tables: elenca tutte le tabelle del database.
- get_table_structure: restituisce la struttura (colonne, tipi) di una o più tabelle. Passa i nomi separati da virgola.

Rispondi sempre in italiano.
Usa list_tables per scoprire le tabelle disponibili, poi get_table_structure per i dettagli se necessario."""


def create_schema_agent(connection_string: str, model: str | None = None):
    """
    Create the schema agent with list_tables and get_table_structure tools.

    Args:
        connection_string: SQLAlchemy connection string for Microsoft SQL Server.
        model: Ollama model name (default from OLLAMA_MODEL env or "llama3.2").

    Returns:
        Compiled agent (CompiledStateGraph) ready for invoke/stream.
    """
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
    tools = create_schema_tools(connection_string)

    return create_agent(
        model=f"ollama:{model}",
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )
