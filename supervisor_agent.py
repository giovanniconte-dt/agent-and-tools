"""Supervisor agent that coordinates schema_explorer and sql_executor workers."""

import os

from langchain.agents import create_agent
from langchain.tools import tool

from agents.sql_agent import create_sql_agent
from agents.schema_agent import create_schema_agent

SYSTEM_PROMPT = """Sei un coordinatore esperto di database SQL.
Hai due worker a disposizione:
- schema_explorer: usa per elencare le tabelle o ottenere la struttura di una tabella. Es: "elenca le tabelle", "struttura della tabella users".
- sql_executor: usa per eseguire query SELECT o UPDATE sui dati. Es: "quanti clienti ci sono", "aggiorna il record X".

Scegli il worker appropriato in base alla richiesta dell'utente.
Per query sui dati, puoi prima usare schema_explorer per conoscere le tabelle disponibili, poi sql_executor per la query.
Rispondi sempre in italiano."""


def _extract_response(result) -> str:
    """Extract response text from agent result."""
    messages = result.get("messages", [])
    last = messages[-1] if messages else None
    if last and hasattr(last, "content"):
        content = last.content
        return content if isinstance(content, str) else str(content)
    return ""


def create_supervisor_agent(connection_string: str, model: str | None = None):
    """
    Create the supervisor agent with schema_explorer and sql_executor worker tools.

    Args:
        connection_string: SQLAlchemy connection string for Microsoft SQL Server.
        model: Ollama model name (default from OLLAMA_MODEL env or "llama3.2").

    Returns:
        Compiled agent (CompiledStateGraph) ready for invoke/stream.
    """
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
    sql_agent = create_sql_agent(connection_string, model)
    schema_agent = create_schema_agent(connection_string, model)

    @tool
    def schema_explorer(request: str) -> str:
        """Usa per elenco tabelle o struttura di una tabella. Es: 'elenca le tabelle', 'struttura della tabella X'."""
        try:
            result = schema_agent.invoke({
                "messages": [{"role": "user", "content": request}]
            })
            return _extract_response(result)
        except Exception as e:
            return f"Errore schema_explorer: {e}"

    @tool
    def sql_executor(request: str) -> str:
        """Usa per query SELECT o UPDATE sui dati. Es: 'quanti clienti ci sono', 'aggiorna...'."""
        try:
            result = sql_agent.invoke({
                "messages": [{"role": "user", "content": request}]
            })
            return _extract_response(result)
        except Exception as e:
            return f"Errore sql_executor: {e}"

    return create_agent(
        model=f"ollama:{model}",
        tools=[schema_explorer, sql_executor],
        system_prompt=SYSTEM_PROMPT,
    )
