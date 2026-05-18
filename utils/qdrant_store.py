"""Qdrant Cloud vector store setup and operations."""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, PayloadSchemaType
from langchain_qdrant import QdrantVectorStore
from utils.embeddings import get_embedding_model

load_dotenv()

COLLECTION_NAME = "rag_documents"
VECTOR_SIZE = 3072  # Gemini gemini-embedding-001 dimension


def get_qdrant_client() -> QdrantClient:
    """Initialize Qdrant Cloud client."""
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    if not url or not api_key:
        raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set")
    return QdrantClient(url=url, api_key=api_key, timeout=120)


def create_collection(client: QdrantClient):
    """Create or recreate the vector collection with role payload index."""
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in collections:
        print(f"Deleting existing collection: {COLLECTION_NAME}")
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

    # Create payload index on 'role' field for fast filtering
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="metadata.role",
        field_schema=PayloadSchemaType.KEYWORD,
    )
    print(f"Created collection: {COLLECTION_NAME} (with role index)")


def get_vector_store(role: str = None) -> QdrantVectorStore:
    """Get LangChain QdrantVectorStore, optionally filtered by role."""
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    embeddings = get_embedding_model()

    return QdrantVectorStore.from_existing_collection(
        url=url,
        api_key=api_key,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )


def build_role_filter(role: str) -> Filter:
    """Build a Qdrant filter for a specific role."""
    return Filter(
        must=[
            FieldCondition(
                key="metadata.role",
                match=MatchValue(value=role),
            )
        ]
    )


def get_collection_info(client: QdrantClient) -> dict:
    """Get collection statistics."""
    try:
        info = client.get_collection(COLLECTION_NAME)
        return {
            "collection": COLLECTION_NAME,
            "vectors_count": info.points_count,
            "points_count": info.points_count,
            "status": str(info.status),
        }
    except Exception as e:
        return {"error": str(e)}
