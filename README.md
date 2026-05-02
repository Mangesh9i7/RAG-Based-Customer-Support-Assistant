# 🤖 RAG Based Customer Support Assistant

A lightweight, intelligent customer support chatbot built using **Retrieval-Augmented Generation (RAG)**.

It ingests a local support dataset (by default a **CSV**) from the backend `data/raw/` folder, stores vector embeddings locally using **ChromaDB (Chroma)**, and answers user queries by combining retrieved context with a powerful **LLM** via the Groq API.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture & Workflow](#architecture--workflow)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Module Breakdown](#module-breakdown)
- [Design Documentation](#design-documentation)
- [Future Enhancements](#future-enhancements)

---

## 🎯 Overview

This project implements a **local-vector, API-powered RAG pipeline**.

It loads a support knowledge base from the backend `RAG_Backend/data/raw/` folder, chunks it, embeds it using a HuggingFace embedding model (`all-MiniLM-L6-v2`), and stores the vectors in a persistent **Chroma** vector database (`RAG_Backend/vector_db/`).

At runtime, user questions trigger a similarity search over the vector store, and the top-k retrieved chunks are fed into a **LangChain** chain backed by **Groq** (`llama-3.1-8b-instant`) to generate answers.

The assistant is designed to:

- Handle **casual greetings** naturally.
- Answer **domain-specific questions** using retrieved context.
- Avoid guessing: if the retrieved context does **not** contain the answer, it triggers a **Human-in-the-Loop (HITL)** response.

> **HITL phrase (exact):**  
> `I don't have the exact information for that right now. Let me connect you with a human support agent who can help.`

---

## ✨ Features

| Feature                        | Description                                                                           |
| ------------------------------ | ------------------------------------------------------------------------------------- |
| 📄 **Data Ingestion**          | Loads supported file types from `RAG_Backend/data/raw/` (default is **CSV**).         |
| 🧠 **Local Embeddings**        | Uses `sentence-transformers` embeddings via `all-MiniLM-L6-v2`.                       |
| 💾 **Persistent Vector Store** | Chroma persists vectors locally in `RAG_Backend/vector_db/`.                          |
| ⚡ **Fast Inference**          | Uses Groq API (`llama-3.1-8b-instant`) for fast responses.                            |
| 🔄 **Smart Prompting**         | Custom prompt enforces greetings and strict HITL fallback (no guessing).              |
| 💬 **Streaming CLI + API**     | CLI streams output chunk-by-chunk; FastAPI streams `/chat` responses to the frontend. |

---

## 🛠 Tech Stack

| Category                   | Technology                                                                                     |
| -------------------------- | ---------------------------------------------------------------------------------------------- |
| **Language**               | Python (backend) + JavaScript/React (frontend)                                                 |
| **LLM Framework**          | LangChain (`langchain-core`, `langchain-community`, `langchain-groq`, `langchain-huggingface`) |
| **LLM Provider**           | [Groq](https://groq.com/) – `llama-3.1-8b-instant`                                             |
| **Embeddings**             | HuggingFace – `all-MiniLM-L6-v2`                                                               |
| **Vector Database**        | Chroma                                                                                         |
| **Data Parsing / Loading** | PyPDF / CSV / Text / Word loaders (selected by file extension in code)                         |
| **Environment Management** | `python-dotenv`                                                                                |

---

## 🏗 Architecture & Workflow

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│   User Input    │─────▶│   CLI / React   │─────▶│  LangChain Chain    │
└─────────────────┘      └──────────────────┘      │  (RAG: src/graph.py)│
                                                   └──────────┬──────────┘
                                                              │
                              ┌───────────────────────────────┘
                              │
                              ▼
         ┌─────────────────────────────────────────────┐
         │  1. Retriever (Chroma + HuggingFace)        │
         │     • Similarity search over vector store  │
         │     • Top-k chunks returned                 │
         └─────────────────────┬───────────────────────┘
                               │
                               ▼
         ┌─────────────────────────────────────────────┐
         │  2. Prompt Template (src/prompts.py)       │
         │     • Injects context + question           │
         │     • Handles greetings                    │
         │     • HITL fallback (no guessing)          │
         └─────────────────────┬───────────────────────┘
                               │
                               ▼
         ┌─────────────────────────────────────────────┐
         │  3. LLM (Groq – llama-3.1-8b-instant)       │
         │     • Generates streamed response          │
         └─────────────────────────────────────────────┘
```

### Data Ingestion Flow (First Run)

Default input is **CSV**:

```
RAG_Backend/data/raw/customer_support_tickets.csv
    │
    ▼
CSVLoader ──▶ Documents
    │
    ▼
RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200)
    │
    ▼
HuggingFaceEmbeddings (all-MiniLM-L6-v2)
    │
    ▼
Chroma (persisted in RAG_Backend/vector_db/)
```

> If `RAG_Backend/vector_db/` already exists and is non-empty, the system loads it instead of re-ingesting.

---

## 📁 Project Structure

```
RAG Based Customer Support Assistant/
│
├── 📄 README.md
│
├── 📁 client/
│   ├── 📄 package.json
│   ├── 📄 vite.config.js
│   └── 📁 src/
│       ├── 📄 main.jsx                     # Routes: / and /chat
│       └── 📁 components/
│           ├── 📁 home/
│           │   └── HomePage.jsx          # Landing UI
│           └── 📁 chat/
│               ├── ChatPage.jsx         # Chat UI + streamed fetch
│               └── ChatPage.css
│
└── 📁 RAG_Backend/
    │
    ├── 📄 main.py                          # Entry point – interactive CLI chat
    ├── 📄 requirements.txt                 # Python dependencies
    ├── 📄 .gitignore                       # Ignores __pycache__, .env, *.pyc
    │
    ├── 📁 src/                             # Core application source code
    │   ├── __init__.py
    │   ├── 📄 api.py                       # FastAPI: POST /chat, GET /
    │   ├── config.py                       # Global constants & file paths
    │   ├── graph.py                        # LangChain RAG pipeline assembly
    │   ├── ingestr.py                      # PDF loading & text chunking logic
    │   ├── prompts.py                      # ChatPromptTemplate for the RAG chain
    │   └── vector_store.py                 # ChromaDB initialization & retriever
    │
    ├── 📁 data/
    │   └── 📁 raw/
    │       └── support_kb.pdf              # Source knowledge base (PDF)
    │
    ├── 📁 vector_db/                       # Persistent ChromaDB vector store
    │   ├── chroma.sqlite3
    │   └── 45804ed9-.../                   # HNSW index segment files
    │
    └── 📁 docs/                            # Design & technical documentation
        ├── High-Level Design (HLD).pdf
        ├── Low-Level Design (LLD).pdf
        └── Technical Documentation.pdf
```

---

## ⚙️ Prerequisites

- **Python 3.x** installed
- A free **Groq API Key** ([get one here](https://console.groq.com/keys))
- A support dataset file inside:
  - `RAG_Backend/data/raw/` (default is `customer_support_tickets.csv`)

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Mangesh9i7/-RAG-Based-Customer-Support-Assistant.git
cd -RAG-Based-Customer-Support-Assistant
```

> If your folder name differs, `cd` into the repo root.

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

#### Backend

```bash
pip install -r RAG_Backend/requirements.txt
```

> The HuggingFace embedding model will download automatically on the first run.

#### Frontend

```bash
cd client
npm install
```

---

## 🔑 Configuration

Create a `.env` file in **`RAG_Backend/`**:

```env
GROQ_API_KEY="your_groq_api_key_here"
```

The application uses `python-dotenv` to load this key at runtime.

### Default Configurations (`RAG_Backend/src/config.py`)

| Constant               | Value                                   | Description                                |
| ---------------------- | --------------------------------------- | ------------------------------------------ |
| `RETRIEVER_K`          | `3`                                     | Number of top chunks retrieved for context |
| `GROQ_MODEL_NAME`      | `llama-3.1-8b-instant`                  | LLM model used via Groq                    |
| `EMBEDDING_MODEL_NAME` | `all-MiniLM-L6-v2`                      | HuggingFace embedding model                |
| `DATA_FILE_PATH`       | `data/raw/customer_support_tickets.csv` | Path to default knowledge base file        |
| `VECTOR_DB_DIR`        | `vector_db/`                            | Directory for persistent Chroma storage    |

---

## 💻 Usage

You can run the system in multiple ways: **Backend API**, **Frontend UI**, and optionally the **CLI chat**.

### 1) Run the Backend API (FastAPI)

From the project root:

```bash
cd RAG_Backend
uvicorn src.api:api --reload --port 8000
```

- Health:
  - `GET http://localhost:8000/health`

### 2) Run the Frontend (React)

From the project root:

```bash
cd client
npm run dev
```

Open:

- `http://localhost:5173/`

The chat UI calls the backend at:

- `http://localhost:8000/chat`

### 3) Run the Backend CLI Chat (Optional)

From the project root:

```bash
cd RAG_Backend
python main.py
```

Example session:

```
Welcome! How can I help you?
Type 'quit' or 'exit' to stop.

User:-  Hello

Thinking...
Hi there! How can I help you today?
--------------------------------------------------

User:-  What is the return policy?

Thinking...
Our return policy allows you to return items within 30 days of purchase...
--------------------------------------------------

User:-  exit
```

- Responses are **streamed** in real-time for a smooth experience.
- Type `quit` or `exit` to stop.
- If the assistant emits the HITL trigger substring, it prints a human routing alert.

---

## 🔍 Module Breakdown

### `RAG_Backend/main.py`

The interactive CLI entry point. It:

- Loads environment variables via `dotenv.load_dotenv()`
- Imports `app` from `src.graph`
- Loops over user questions
- Streams the answer chunk-by-chunk using `app.stream(question)`
- Checks whether the HITL trigger phrase appears in the streamed output

### `RAG_Backend/src/config.py`

Centralized configuration module defining:

- retrieval hyperparameter `RETRIEVER_K`
- model names
- default dataset path `DATA_FILE_PATH`
- `VECTOR_DB_DIR` for Chroma persistence

### `RAG_Backend/src/api.py`

FastAPI server:

- `POST /chat`: wraps `rag_chain.stream()` in a `StreamingResponse`
- `GET /health`: status response
- Enables CORS for the frontend origin:
  - `http://localhost:5173`

### `RAG_Backend/src/graph.py`

Assembles the executable LangChain pipeline (`app`):

- `context` is built as: `retriever | format_docs`
- `question` is passed through via `RunnablePassthrough()`
- the pipeline is:
  - `rag_prompt` → `llm` → `StrOutputParser()`

### `RAG_Backend/src/ingestr.py`

Handles data ingestion:

- Loads the dataset based on extension of `DATA_FILE_PATH`:
  - CSV, PDF, TXT, DOC/DOCX supported
- Chunks documents with:
  - `chunk_size=1000`
  - `chunk_overlap=200`

### `RAG_Backend/src/vector_store.py`

Manages the vector database lifecycle:

- Builds `HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)`
- If `VECTOR_DB_DIR` exists and is non-empty:
  - loads existing Chroma
- Else:
  - ingests + embeds + creates Chroma + persists it
- Returns `vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})`

### `RAG_Backend/src/prompts.py`

Defines `rag_prompt` with strict rules:

1. **Casual Chat**: greetings are answered naturally without referencing documents/context.
2. **Answering Questions**: it uses retrieved context when the answer exists in it.
3. **HUMAN-IN-THE-LOOP (HITL)**:
   - if the context does NOT contain the answer:
   - it does **not** guess
   - it returns exactly:
     `I don't have the exact information for that right now. Let me connect you with a human support agent who can help.`
4. It avoids meta phrases like “Based on the context...”.

---

## 📚 Design Documentation

The `docs/` folder contains comprehensive design artifacts:
| Document | Purpose |
| -------- | ------- |
| `High-Level Design (HLD).pdf` | System architecture, component interactions, and technology choices |
| `Low-Level Design (LLD).pdf` | Detailed module-level design, data flow, and lower-level details |
| `Technical Documentation.pdf` | API references, operational guidelines, deployment notes |

---

## 🔮 Future Enhancements

- [ ] **Web Interface Upgrades**: show HITL state explicitly in UI
- [ ] **Multi-Document Support**: ingest multiple PDFs/CSVs and merge indexes
- [ ] **Conversation Memory**: send chat history to backend for better multi-turn support
- [ ] **Re-ranking**: integrate reranking to improve retrieval quality
- [ ] **Re-index API**: admin endpoint to rebuild embeddings/vector store
- [ ] **Dockerization**: dockerize backend + frontend
- [ ] **CI/CD Pipeline**: automated testing and quality checks

---

## 🙋 Support

For questions or issues:

- Check backend logs (Uvicorn terminal)
- Check frontend console logs (browser devtools)
- Refer to `docs/` and the design PDFs for deeper implementation notes

---

<p align="center">
  <b>Built with ❤️ using LangChain, Groq & ChromaDB</b>
</p>
