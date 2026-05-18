"""RAG retrieval and generation chain using Gemini LLM."""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from utils.qdrant_store import get_vector_store, build_role_filter

load_dotenv()

RAG_PROMPT_TEMPLATE = """You are a helpful assistant that answers questions based on the provided context from documents.

Use ONLY the following context to answer the question. If the context doesn't contain enough information to answer, say so clearly.

You are answering as the role: {role}

Context from documents:
{context}

Question: {question}

Provide a clear, detailed answer based on the context. At the end, list the source documents used."""


def format_docs(docs):
    """Format retrieved documents into a context string."""
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        source = os.path.basename(source)
        formatted.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)


def get_source_names(docs):
    """Extract unique source filenames from retrieved documents."""
    sources = set()
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        sources.add(os.path.basename(source))
    return sorted(sources)


def query_rag(question: str, role: str = None, top_k: int = 5) -> dict:
    """Run a RAG query with optional role-based filtering."""
    vector_store = get_vector_store()

    # Build search kwargs with optional role filter
    search_kwargs = {"k": top_k}
    if role and role != "all":
        search_kwargs["filter"] = build_role_filter(role)

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs,
    )

    retrieved_docs = retriever.invoke(question)

    if not retrieved_docs:
        return {
            "answer": "I couldn't find any relevant information in the documents assigned to your role.",
            "sources": [],
            "chunks_used": 0,
            "role": role or "all",
        }

    context = format_docs(retrieved_docs)
    sources = get_source_names(retrieved_docs)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
    )

    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()

    role_display = role.upper().replace("_", " ") if role and role != "all" else "All Access"

    answer = chain.invoke({
        "context": context,
        "question": question,
        "role": role_display,
    })

    return {
        "answer": answer,
        "sources": sources,
        "chunks_used": len(retrieved_docs),
        "role": role or "all",
    }
