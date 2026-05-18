"""Flask backend for RAG chatbot with Qdrant Cloud and Role-Based Access."""
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from utils.rag_chain import query_rag
from utils.qdrant_store import get_qdrant_client, get_collection_info
from utils.roles import get_all_roles, ROLES
from ingest import ingest

load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the chat UI."""
    return render_template("index.html")


@app.route("/api/roles", methods=["GET"])
def api_roles():
    """Return all available roles."""
    return jsonify(get_all_roles())


@app.route("/api/query", methods=["POST"])
def api_query():
    """Handle user query with role-based filtering."""
    data = request.get_json()
    question = data.get("question", "").strip()
    role = data.get("role", "all")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        result = query_rag(question, role=role, top_k=5)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ingest", methods=["POST"])
def api_ingest():
    """Trigger document re-ingestion."""
    try:
        result = ingest()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def api_stats():
    """Get Qdrant collection statistics."""
    try:
        client = get_qdrant_client()
        info = get_collection_info(client)
        docs_dir = os.path.join(os.path.dirname(__file__), "documents")
        doc_count = len(os.listdir(docs_dir)) if os.path.exists(docs_dir) else 0
        info["documents_in_folder"] = doc_count
        info["roles_count"] = len(ROLES)
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
