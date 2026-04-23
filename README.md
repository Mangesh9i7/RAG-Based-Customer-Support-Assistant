# 🤖 RAG Based Customer Support Assistant

A lightweight, intelligent customer support chatbot built using **Retrieval-Augmented Generation (RAG)**. It ingests a PDF knowledge base, stores vector embeddings locally using **ChromaDB**, and answers user queries by combining retrieved context with a powerful **LLM** via the Groq API.

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

This project implements a fully local-vector, API-powered RAG pipeline. It loads a support knowledge base from a PDF, chunks the content, embeds it using a free Hugging Face model, and stores the vectors in a persistent **ChromaDB** instance. At runtime, user questions trigger a similarity search over the vector store, and the top-k retrieved chunks are fed into a **LangChain** chain backed by **Groq's `llama-3.1-8b-instant`** model to generate accurate, contextual answers.

The assistant is designed to:

- Handle **casual greetings** naturally.
- Answer **domain-specific questions** using the knowledge base.
- Fall back to **general knowledge** when the context is irrelevant.

---

## ✨ Features

| Feature                        | Description                                                                                     |
| ------------------------------ | ----------------------------------------------------------------------------------------------- |
| 📄 **PDF Ingestion**           | Automatically loads and splits PDF documents into manageable chunks.                            |
| 🧠 **Local Embeddings**        | Uses `sentence-transformers/all-MiniLM-L6-v2` for free, fast, local embedding generation.       |
| 💾 **Persistent Vector Store** | ChromaDB persists vectors locally; no re-ingestion needed after the first run.                  |
| ⚡ **Fast Inference**          | Leverages Groq's API for high-speed responses from `llama-3.1-8b-instant`.                      |
| 🔄 **Smart Prompting**         | Custom RAG prompt handles greetings, contextual Q&A, and general-knowledge fallback gracefully. |
| 💬 **Streaming CLI**           | Interactive command-line interface with real-time streamed responses.                           |

---

## 🛠 Tech Stack

| Category                   | Technology                                                                                     |
| -------------------------- | ---------------------------------------------------------------------------------------------- |
| **Language**               | Python 3.x                                                                                     |
| **LLM Framework**          | LangChain (`langchain-core`, `langchain-community`, `langchain-groq`, `langchain-huggingface`) |
| **LLM Provider**           | [Groq](https://groq.com/) – `llama-3.1-8b-instant`                                             |
| **Embeddings**             | HuggingFace – `all-MiniLM-L6-v2`                                                               |
| **Vector Database**        | ChromaDB                                                                                       |
| **PDF Parsing**            | PyPDFLoader (`pypdf`)                                                                          |
| **Environment Management** | `python-dotenv`                                                                                |

---

## 🏗 Architecture & Workflow

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│   User Input    │─────▶│   CLI (main.py)  │─────▶│  LangChain Chain    │
└─────────────────┘      └──────────────────┘      │  (src/graph.py)     │
                                                   └──────────┬──────────┘
                                                              │
                              ┌───────────────────────────────┘
                              │
                              ▼
         ┌─────────────────────────────────────────────┐
         │  1. Retriever (ChromaDB + HuggingFace)      │
         │     • Similarity search over vector DB      │
         │     • Top-k chunks returned                 │
         └─────────────────────┬───────────────────────┘
                               │
                               ▼
         ┌─────────────────────────────────────────────┐
         │  2. Prompt Template (src/prompts.py)        │
         │     • Injects context + question            │
         │     • Handles greetings & fallback          │
         └─────────────────────┬───────────────────────┘
                               │
                               ▼
         ┌─────────────────────────────────────────────┐
         │  3. LLM (Groq – llama-3.1-8b-instant)       │
         │     • Generates final streamed response     │
         └─────────────────────────────────────────────┘
```

### Data Ingestion Flow (First Run)

```
PDF (data/raw/support_kb.pdf)
    │
    ▼
PyPDFLoader ──▶ Documents
    │
    ▼
RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200)
    │
    ▼
HuggingFaceEmbeddings (all-MiniLM-L6-v2)
    │
    ▼
ChromaDB (persisted in vector_db/)
```

---

## 📁 Project Structure

```
RAG Based Customer Support Assistant/
│
├── 📄 main.py                          # Entry point – interactive CLI chat
├── 📄 requirements.txt                 # Python dependencies
├── 📄 .gitignore                       # Ignores __pycache__, .env, *.pyc
│
├── 📁 src/                             # Core application source code
│   ├── __init__.py
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

- **Python 3.9+** installed on your system
- A free **Groq API Key** ([get one here](https://console.groq.com/keys))
- The knowledge base PDF placed at `data/raw/support_kb.pdf`

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Mangesh9i7/RAG-Based-Customer-Support-Assistant.git
cd "RAG Based Customer Support Assistant"
```

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

```bash
pip install -r requirements.txt
```

> The `sentence-transformers` model (`all-MiniLM-L6-v2`) will be downloaded automatically on the first run.

---

## 🔑 Configuration

Create a `.env` file in the **project root** and add your Groq API key:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

The application uses `python-dotenv` to load this key at runtime.

### Default Configurations (`src/config.py`)

| Constant               | Value                     | Description                                |
| ---------------------- | ------------------------- | ------------------------------------------ |
| `RETRIEVER_K`          | `3`                       | Number of top chunks retrieved for context |
| `GROQ_MODEL_NAME`      | `llama-3.1-8b-instant`    | LLM model used via Groq                    |
| `EMBEDDING_MODEL_NAME` | `all-MiniLM-L6-v2`        | HuggingFace sentence-transformer model     |
| `PDF_FILE_PATH`        | `data/raw/support_kb.pdf` | Path to the knowledge base PDF             |
| `VECTOR_DB_DIR`        | `vector_db/`              | Directory for persistent ChromaDB storage  |

---

## 💻 Usage

Run the application from the project root:

```bash
python main.py
```

### Example Session

```
Welcome! How can i help you?
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

- Responses are **streamed** in real-time for a smooth user experience.
- Type `quit` or `exit` to terminate the session.

---

## 🔍 Module Breakdown

### `main.py`

The application entry point. It:

- Loads environment variables via `dotenv`.
- Imports the compiled LangChain `app` from `src.graph`.
- Runs an infinite loop to accept user input.
- Streams the LLM response chunk-by-chunk to the terminal.

### `src/config.py`

Centralized configuration module defining:

- Absolute base directory resolution.
- File paths for vector DB, raw data, and PDF.
- Model names and retrieval hyperparameters.

### `src/ingestr.py`

Handles document ingestion:

- **`load_and_chunk_pdf()`**: Loads the PDF using `PyPDFLoader`, then splits pages into overlapping chunks using `RecursiveCharacterTextSplitter` (chunk_size=`1000`, overlap=`200`).

### `src/vector_store.py`

Manages the vector database lifecycle:

- **`get_retriever()`**:
  - Checks if a persisted ChromaDB exists in `vector_db/`.
  - If found, loads it directly.
  - If not found, triggers `load_and_chunk_pdf()`, embeds the chunks with `HuggingFaceEmbeddings`, creates a new ChromaDB, and persists it.
  - Returns a retriever configured with `search_kwargs={"k": RETRIEVER_K}`.

### `src/prompts.py`

Defines the `rag_prompt` (`ChatPromptTemplate`) with strict instructions:

1. **Casual Chat**: Respond warmly to greetings without referencing documents.
2. **Answer from Context**: Use retrieved chunks when relevant.
3. **General Knowledge Fallback**: Ignore irrelevant context and answer from internal LLM knowledge.
4. **No Meta-Phrases**: Avoid saying "Based on the context..." or similar.

### `src/graph.py`

Assembles the executable LangChain pipeline (`app`):

```python
app = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)
```

- **Retriever → Formatter**: Fetches top-k documents and joins them into a single context string.
- **RunnablePassthrough**: Passes the raw user question through.
- **Prompt → LLM → Parser**: Generates and parses the final string output.

---

## 📚 Design Documentation

The `docs/` folder contains comprehensive design artifacts:

| Document                      | Purpose                                                             |
| ----------------------------- | ------------------------------------------------------------------- |
| `High-Level Design (HLD).pdf` | System architecture, component interactions, and technology choices |
| `Low-Level Design (LLD).pdf`  | Detailed module-level design, class diagrams, and data flow         |
| `Technical Documentation.pdf` | API references, deployment notes, and operational guidelines        |

> Refer to these documents for deeper insight into the system's design philosophy and implementation details.

---

## 🔮 Future Enhancements

- [ ] **Web Interface**: Replace the CLI with a Streamlit or Gradio frontend.
- [ ] **Multi-Document Support**: Extend ingestion to handle multiple PDFs, Word docs, and web pages.
- [ ] **Conversation Memory**: Add chat history awareness for multi-turn contextual dialogues.
- [ ] **Re-ranking**: Integrate a cross-encoder re-ranker to improve retrieval quality.
- [ ] **Dockerization**: Containerize the application for seamless deployment.
- [ ] **CI/CD Pipeline**: Add automated testing and deployment via GitHub Actions.

---

## 📄 License

_Add your license here (e.g., MIT, Apache 2.0)_

---

## 🙋 Support

For questions or issues, please open an issue in the repository or refer to the technical documentation in the `docs/` folder.

---

<p align="center">
  <b>Built with ❤️ using LangChain, Groq & ChromaDB</b>
</p>
