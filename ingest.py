"""Document ingestion pipeline - loads, chunks, embeds, and stores in Qdrant Cloud."""
import os
import time
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from utils.loader import load_all_documents
from utils.chunker import chunk_documents
from utils.embeddings import get_embedding_model
from utils.qdrant_store import get_qdrant_client, create_collection, COLLECTION_NAME, get_collection_info

load_dotenv()

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")


def ingest(docs_dir: str = DOCUMENTS_DIR) -> dict:
    """Run the full ingestion pipeline."""
    print("=" * 60)
    print("RAG DOCUMENT INGESTION PIPELINE")
    print("=" * 60)

    # Step 1: Load documents
    print("\n[1/4] Loading documents...")
    start = time.time()
    documents = load_all_documents(docs_dir)
    if not documents:
        return {"error": "No documents found", "status": "failed"}
    load_time = time.time() - start
    print(f"  Time: {load_time:.1f}s")

    # Step 2: Chunk documents
    print("\n[2/4] Chunking documents...")
    start = time.time()
    chunks = chunk_documents(documents, chunk_size=500, chunk_overlap=100)
    chunk_time = time.time() - start
    print(f"  Time: {chunk_time:.1f}s")

    # Step 3: Create/recreate Qdrant collection
    print("\n[3/4] Setting up Qdrant Cloud collection...")
    client = get_qdrant_client()
    create_collection(client)

    # Step 4: Embed and store in Qdrant
    print("\n[4/4] Embedding and storing vectors in Qdrant Cloud...")
    start = time.time()
    embeddings = get_embedding_model()

    # Use LangChain's QdrantVectorStore to add documents
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )

    # Add documents in small batches with rate limit protection
    batch_size = 5   # smaller batch → fewer embed calls per minute
    total_batches = (len(chunks) - 1) // batch_size + 1
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_num = i // batch_size + 1

        # Retry on quota errors
        for attempt in range(3):
            try:
                vector_store.add_documents(batch)
                print(f"  Stored batch {batch_num}/{total_batches} ({len(batch)} chunks)")
                break
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                    wait = 65
                    print(f"  Rate limit hit on batch {batch_num}, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    raise

        # Always sleep between batches to avoid hitting 100 req/min limit
        if i + batch_size < len(chunks):
            time.sleep(2)

    embed_time = time.time() - start
    print(f"  Time: {embed_time:.1f}s")

    # Get final stats
    info = get_collection_info(client)

    result = {
        "status": "success",
        "documents_loaded": len(documents),
        "chunks_created": len(chunks),
        "vectors_stored": info.get("vectors_count", "unknown"),
        "collection": COLLECTION_NAME,
        "load_time": f"{load_time:.1f}s",
        "chunk_time": f"{chunk_time:.1f}s",
        "embed_time": f"{embed_time:.1f}s",
    }

    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    for k, v in result.items():
        print(f"  {k}: {v}")

    return result


if __name__ == "__main__":
    ingest()
