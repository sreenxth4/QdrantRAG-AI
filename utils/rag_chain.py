"""RAG retrieval and generation chain using Gemini LLM."""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from utils.qdrant_store import get_vector_store

load_dotenv()

RAG_PROMPT_TEMPLATE = """You are a helpful assistant that answers questions based on the provided context from documents.

Use ONLY the following context to answer the question. If the context doesn't contain enough information to answer, say so clearly.

Context from documents:
{context}

Question: {question}

Provide a clear, detailed answer based on the context. At the end, list the source documents used."""


def format_docs(docs):
    """Format retrieved documents into a context string."""
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        # Extract just the filename
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


def query_rag(question: str, top_k: int = 5) -> dict:
    """Run a RAG query: retrieve relevant chunks and generate an answer."""
    # Get vector store and create retriever
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )

    # Retrieve relevant documents
    retrieved_docs = retriever.invoke(question)

    if not retrieved_docs:
        return {
            "answer": "I couldn't find any relevant information in the documents to answer your question.",
            "sources": [],
            "chunks_used": 0,
        }

    # Format context
    context = format_docs(retrieved_docs)
    sources = get_source_names(retrieved_docs)

    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
    )

    # Create prompt
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

    # Build and run chain
    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke({
        "context": context,
        "question": question,
    })

    return {
        "answer": answer,
        "sources": sources,
        "chunks_used": len(retrieved_docs),
    }
