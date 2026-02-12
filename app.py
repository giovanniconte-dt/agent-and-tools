"""Flask REST API for the SQL agent."""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from agent import create_sql_agent
from config import get_connection_string

load_dotenv()

app = Flask(__name__)
conn_string = get_connection_string()
agent = create_sql_agent(conn_string)


def _extract_response_text(result):
    """Extract response text from agent result."""
    messages = result.get("messages", [])
    last = messages[-1] if messages else None
    if last and hasattr(last, "content"):
        content = last.content
        return content if isinstance(content, str) else str(content)
    return ""


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat request. Body: {"message": "..."} or {"query": "..."}."""
    data = request.get_json() or {}
    message = data.get("message") or data.get("query") or ""

    if not message.strip():
        return jsonify({"error": "message or query is required"}), 400

    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": message}]
        })
        text = _extract_response_text(result)
        return jsonify({"response": text or "(nessuna risposta)"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "").lower() in ("1", "true", "yes")
    app.run(host=host, port=port, debug=debug)
