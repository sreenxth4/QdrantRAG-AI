# 🤖 QdrantRAG-AI — RAG Chatbot with Qdrant Cloud & Google Gemini

A production-grade **Retrieval-Augmented Generation (RAG)** chatbot that ingests documents, stores vector embeddings in **Qdrant Cloud**, and answers questions using **Google Gemini** LLM with source citations.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask)
![Qdrant](https://img.shields.io/badge/Qdrant-Cloud-DC382D?logo=qdrant)
![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google)
![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C)

---

## 📌 Overview

This system implements a complete RAG pipeline:

```
Documents → Chunking → Embeddings → Qdrant Cloud → Similarity Search → Gemini LLM → Answer + Sources
```

**Key Features:**
- 📄 Ingests **100 documents** (PDF, TXT, MD formats supported)
- 🔢 Chunks and embeds documents using **Gemini Embedding Model**
- ☁️ Stores vectors in **Qdrant Cloud** (production-grade, persistent)
- 🔍 Retrieves top-K relevant chunks via cosine similarity search
- 🧠 Generates answers using **Google Gemini LLM** with context
- 📚 Returns **source document citations** with every answer
- 🎨 Premium **dark-themed web UI** with glassmorphism design

---

## 🏗️ Architecture

```
                ┌─────────────────────┐
                │   100 Documents     │
                │ (PDF / TXT / MD)    │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │ Document Loader     │
                │ PyPDF / TextLoader  │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │ Text Chunking       │
                │ RecursiveCharacter   │
                │ TextSplitter        │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │ Embedding Model     │
                │ Gemini Embedding    │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │ Qdrant Cloud        │
                │ Vector Database     │
                └─────────┬───────────┘
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
      User asks query          Query → Embedding
             │                         │
             └────────────┬────────────┘
                          ▼
                ┌─────────────────────┐
                │ Similarity Search   │
                │ Top-5 Chunks        │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │ Gemini LLM          │
                │ Generate Answer     │
                └─────────┬───────────┘
                          ▼
                ┌─────────────────────┐
                │ Answer + Sources    │
                └─────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Backend** | Python + Flask |
| **Vector Database** | Qdrant Cloud |
| **Embeddings** | Google Gemini (`gemini-embedding-001`, 3072-dim) |
| **LLM** | Google Gemini (`gemini-2.5-flash-lite`) |
| **RAG Framework** | LangChain |
| **Document Loaders** | PyPDFLoader, TextLoader |
| **Text Splitting** | RecursiveCharacterTextSplitter |
| **Frontend** | HTML, CSS, JavaScript |

---

## 📂 Project Structure

```
rag-qdrant/
│
├── app.py                    # Flask server (main entry point)
├── ingest.py                 # Document ingestion pipeline
├── generate_docs.py          # Generate 100 sample documents
├── requirements.txt          # Python dependencies
├── .env                      # API keys (not tracked in git)
├── .gitignore
│
├── documents/                # 100 text documents
│     ├── ai_machine_learning.txt
│     ├── google_gemini.txt
│     ├── quantum_computing.txt
│     └── ... (100 files)
│
├── utils/
│     ├── __init__.py
│     ├── loader.py           # Document loading (PDF, TXT, MD)
│     ├── chunker.py          # Text chunking logic
│     ├── embeddings.py       # Gemini embedding model setup
│     ├── qdrant_store.py     # Qdrant Cloud client & operations
│     └── rag_chain.py        # RAG retrieval + generation chain
│
├── static/
│     ├── style.css           # Premium dark theme UI
│     └── script.js           # Frontend chat logic
│
└── templates/
      └── index.html          # Chat interface
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Google Gemini API Key ([Get one here](https://aistudio.google.com/apikey))
- Qdrant Cloud Account ([Sign up here](https://cloud.qdrant.io))

### 1. Clone the Repository

```bash
git clone https://github.com/sreenxth4/QdrantRAG-AI.git
cd QdrantRAG-AI
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
QDRANT_URL=https://your-cluster-id.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
```

### 4. Generate Sample Documents (Optional)

If you don't have your own documents:

```bash
python generate_docs.py
```

This creates **100 text documents** covering AI, technology, science, history, space, business, health, and environment.

### 5. Ingest Documents into Qdrant Cloud

```bash
python ingest.py
```

**Output:**
```
============================================================
RAG DOCUMENT INGESTION PIPELINE
============================================================

[1/4] Loading documents...
  Total documents loaded: 100

[2/4] Chunking documents...
  Split 100 documents into 100 chunks

[3/4] Setting up Qdrant Cloud collection...
  Created collection: rag_documents

[4/4] Embedding and storing vectors in Qdrant Cloud...
  Stored batch 1/5 (20 chunks)
  Stored batch 2/5 (20 chunks)
  Stored batch 3/5 (20 chunks)
  Stored batch 4/5 (20 chunks)
  Stored batch 5/5 (20 chunks)

============================================================
INGESTION COMPLETE
============================================================
  status: success
  documents_loaded: 100
  chunks_created: 100
```

### 6. Start the Server

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 💬 Usage

### Web UI
- Type a question in the chat input
- Press Enter or click the send button
- The AI retrieves relevant document chunks and generates an answer
- Source documents are displayed with each response
- Click **Reindex** to re-ingest all documents

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Chat UI |
| `POST` | `/api/query` | Ask a question — returns answer + sources |
| `POST` | `/api/ingest` | Trigger document re-ingestion |
| `GET` | `/api/stats` | Get collection stats (doc count, vector count) |

**Example API call:**
```bash
curl -X POST http://127.0.0.1:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Which organization created the AI model that processes text and images?"}'
```

**Response:**
```json
{
  "answer": "Google DeepMind created Gemini, a multimodal AI model...",
  "sources": ["google_gemini.txt", "generative_ai.txt"],
  "chunks_used": 5
}
```

---

## 🧪 Example: Indirect Question Test

**Document content** (`google_gemini.txt`):
> "Gemini is a multimodal AI model developed by Google DeepMind. It can process text, images, audio, and video simultaneously."

**Indirect question:**
> "Which organization created the AI model that can process both text and images simultaneously?"

**RAG answer:**
> "Based on the documents, **Google DeepMind** created the AI model called **Gemini**, which can process text, images, audio, and video simultaneously."

**Sources cited:** `google_gemini.txt`, `generative_ai.txt`

This demonstrates the system's ability to:
- ✅ Retrieve relevant chunks via semantic search
- ✅ Reason over context to answer indirect questions
- ✅ Cite source documents

---

## 🔧 Configuration

| Parameter | File | Default |
|---|---|---|
| Chunk size | `utils/chunker.py` | 500 characters |
| Chunk overlap | `utils/chunker.py` | 100 characters |
| Top-K retrieval | `utils/rag_chain.py` | 5 chunks |
| Embedding model | `utils/embeddings.py` | `gemini-embedding-001` |
| LLM model | `utils/rag_chain.py` | `gemini-2.5-flash-lite` |
| Vector dimensions | `utils/qdrant_store.py` | 3072 |
| Distance metric | `utils/qdrant_store.py` | Cosine |

---

## 📊 Document Topics (100 Documents)

| Category | Count | Examples |
|---|---|---|
| AI & Machine Learning | 15 | Neural networks, NLP, computer vision, GANs |
| Technology & Computing | 15 | Cloud, DevOps, Python, JavaScript, databases |
| Science & Physics | 10 | Quantum mechanics, relativity, particle physics |
| History & World Events | 10 | World War 2, Renaissance, French Revolution |
| Space & Astronomy | 10 | Black holes, exoplanets, Mars, Hubble |
| Business & Economics | 10 | Stock market, venture capital, fintech |
| Medicine & Health | 10 | Genetics, vaccines, mental health, telemedicine |
| Environment & Climate | 10 | Climate change, renewable energy, biodiversity |
| Emerging Tech | 10 | Robotics, AR/VR, 3D printing, nanotechnology |

---

## 🙏 Acknowledgements

- [Qdrant](https://qdrant.tech/) — High-performance vector database
- [Google Gemini](https://ai.google.dev/) — Embeddings and LLM
- [LangChain](https://langchain.com/) — RAG framework
- [Flask](https://flask.palletsprojects.com/) — Web framework

---

## 📄 License

This project is for educational and assignment purposes.
