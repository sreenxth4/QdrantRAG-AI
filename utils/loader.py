"""Document loader utility - loads PDFs, TXT, and MD files from a directory."""
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from utils.roles import get_role_for_document


def load_single_file(filepath: str) -> list[Document]:
    """Load a single file based on its extension."""
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".pdf":
            loader = PyPDFLoader(filepath)
            return loader.load()
        elif ext in (".txt", ".md", ".text"):
            loader = TextLoader(filepath, encoding="utf-8")
            return loader.load()
        else:
            print(f"  Skipping unsupported file: {filepath}")
            return []
    except Exception as e:
        print(f"  Error loading {filepath}: {e}")
        return []


def load_all_documents(directory: str) -> list[Document]:
    """Load all supported documents from a directory and inject role metadata."""
    all_docs = []
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return all_docs

    files = sorted(os.listdir(directory))
    print(f"Found {len(files)} files in {directory}")

    for filename in files:
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            docs = load_single_file(filepath)
            if docs:
                # Inject role metadata into each document
                role = get_role_for_document(filename)
                for doc in docs:
                    doc.metadata["role"] = role
                    doc.metadata["filename"] = filename
                print(f"  Loaded: {filename} ({len(docs)} page(s)) -> role: {role}")
                all_docs.extend(docs)

    print(f"\nTotal documents loaded: {len(all_docs)}")
    return all_docs
