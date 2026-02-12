"""Create the SQL agent with read and write tools."""

import os

from langchain.agents import create_agent

from tools import create_sql_tools

SYSTEM_PROMPT = """Sei un assistente esperto di database SQL.
Hai accesso a due tool:
- read_sql: usa per query di lettura (SELECT). Passa una query SQL SELECT valida.
- write_sql: usa per modificare i dati (UPDATE). Passa una query SQL valida.

Genera le query SQL appropriate in base alle richieste dell'utente.
Rispondi sempre in italiano.
Se non conosci lo schema delle tabelle, genera query ragionevoli o chiedi chiarimenti."""


def create_sql_agent(connection_string: str, model: str | None = None):
    """
    Create the SQL agent with read and write tools.

    Args:
        connection_string: SQLAlchemy connection string for Microsoft SQL Server.
        model: Ollama model name (default from OLLAMA_MODEL env or "llama3.2").

    Returns:
        Compiled agent (CompiledStateGraph) ready for invoke/stream.
    """
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
    tools = create_sql_tools(connection_string)

    return create_agent(
        model=f"ollama:{model}",
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )
