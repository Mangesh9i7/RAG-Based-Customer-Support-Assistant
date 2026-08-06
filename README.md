# RAG Customer Support Assistant

A full-stack, Retrieval-Augmented Generation (RAG) support chatbot. It answers customer questions from your own knowledge base, streams responses token-by-token, and gracefully hands off to a human agent when it doesn't know the answer — instead of guessing.

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white">
  <img alt="React" src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black">
  <img alt="LangChain" src="https://img.shields.io/badge/LangChain-RAG%20pipeline-1C3C3C">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
</p>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Setup (without Docker)](#local-setup-without-docker)
  - [Run with Docker Compose](#run-with-docker-compose)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [API Reference](#api-reference)
- [Adding Your Own Knowledge Base](#adding-your-own-knowledge-base)
- [Deployment](#deployment)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

This project implements a customer-support chatbot backed by **Retrieval-Augmented Generation**: instead of relying purely on an LLM's parametric knowledge (which leads to hallucination), the system retrieves relevant passages from your own support documents at query time and grounds the model's answer in that retrieved context.

The assistant is explicitly designed with a **human-in-the-loop (HITL) fallback**: if the retrieved context doesn't actually contain the answer, the model is instructed — via prompt design, not a separate classifier — to say so and hand off to a human, rather than fabricate a plausible-sounding but wrong answer. This is the behavior you actually want in a support context, where a confidently wrong answer is worse than an honest "I don't know."

## Key Features

- 🔍 **Retrieval-Augmented Generation** — answers are grounded in your own documents, not just the LLM's training data.
- 📄 **Multi-format ingestion** — automatically loads `.pdf`, `.txt`, `.docx`/`.doc`, or `.csv` files from `data/raw/`.
- ⚡ **Streaming responses** — tokens are streamed from the LLM through FastAPI to the browser as they're generated, not returned all at once.
- 🤝 **Human-in-the-loop fallback** — when the knowledge base doesn't contain the answer, the assistant says so explicitly and signals a handoff, instead of hallucinating.
- 💬 **Casual conversation handling** — greetings and small talk are handled naturally without forcing a document lookup.
- 🎨 **Modern chat UI** — a React + Vite single-page app with a collapsible conversation sidebar.
- 🐳 **Container-ready** — ships with Dockerfiles for both a combined single-container deployment and a decoupled `docker-compose` setup (frontend + backend as separate services, behind an nginx reverse proxy).

## Architecture

```
┌─────────────────┐        HTTP (streamed)        ┌──────────────────────┐
│   React + Vite   │ ─────────────────────────────▶ │   FastAPI backend    │
│   (nginx, :80)   │ ◀───────────────────────────── │   (uvicorn, :5000)   │
└─────────────────┘                                 └──────────┬───────────┘
                                                                 │
                                                     ┌───────────┴───────────┐
                                                     │   LangChain pipeline   │
                                                     │  (LCEL Runnable chain) │
                                                     └───────────┬───────────┘
                                                                 │
                                    ┌────────────────────────────┼────────────────────────────┐
                                    │                             │                             │
                          ┌─────────▼─────────┐        ┌──────────▼──────────┐       ┌──────────▼──────────┐
                          │   FAISS retriever  │        │  HF embedding model  │       │   Groq LLM (Llama)   │
                          │  (local vector db) │        │ (Inference API call) │       │  llama-3.1-8b-instant│
                          └────────────────────┘        └──────────────────────┘       └───────────────────────┘
```

**Request flow:**

1. The user asks a question in the chat UI.
2. The frontend sends `POST /chat` (proxied by nginx to the backend in the Docker Compose setup).
3. The question is embedded and compared against a FAISS vector index built from your knowledge base.
4. The top-_k_ matching chunks are injected into a structured prompt alongside the question.
5. The Groq-hosted Llama model generates an answer grounded in that context, streamed back token by token.
6. If the retrieved context doesn't answer the question, the model returns a fixed hand-off message instead of guessing.

## Tech Stack

| Layer            | Technology                                                                                             |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| Frontend         | React 19, React Router, Vite, vanilla CSS                                                              |
| Backend          | FastAPI, Uvicorn, Pydantic                                                                             |
| Orchestration    | LangChain (LCEL — LangChain Expression Language)                                                       |
| LLM              | Groq API — `llama-3.1-8b-instant`                                                                      |
| Embeddings       | Hugging Face Inference API — `sentence-transformers/all-MiniLM-L6-v2`                                  |
| Vector store     | FAISS (local, on-disk index)                                                                           |
| Document loaders | `PyPDFLoader`, `TextLoader`, `UnstructuredWordDocumentLoader`, `CSVLoader` (via `langchain-community`) |
| Serving          | nginx (frontend), Uvicorn (backend)                                                                    |
| Containerization | Docker, Docker Compose                                                                                 |

## Project Structure

```
RAG-Based-Customer-Support-Assistant/
├── Dockerfile                    # Combined single-container build (e.g. Hugging Face Spaces)
├── docker-compose.yml            # Two-service local/dev deployment (frontend + backend)
│
├── client/                       # React + Vite frontend
│   ├── Dockerfile                # nginx-based build + reverse proxy config
│   ├── nginx.conf                # Proxies /chat, /health to the backend service
│   ├── src/
│   │   ├── main.jsx
│   │   └── components/chat/ChatPage.jsx
│   └── package.json
│
└── RAG_Backend/                  # FastAPI backend
    ├── Dockerfile
    ├── main.py                   # CLI entry point (local terminal chat, for quick testing)
    ├── requirements.txt
    ├── data/raw/                 # Your source knowledge base documents go here
    ├── docs/                     # Design docs (HLD, LLD, technical documentation)
    ├── vector_db/                # Generated FAISS index (index.faiss, index.pkl)
    └── src/
        ├── api.py                # FastAPI app: /chat, /health routes
        ├── config.py             # Paths, model names, retriever settings
        ├── graph.py              # LCEL chain: retrieve → prompt → LLM → parse
        ├── ingestr.py            # Document loading + chunking
        ├── prompts.py            # RAG system prompt (incl. HITL fallback logic)
        └── vector_store.py       # FAISS index build/load + retriever
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 20+
- A free [Groq API key](https://console.groq.com/keys)
- A free [Hugging Face access token](https://huggingface.co/settings/tokens) (used for the embeddings Inference API call)
- Docker + Docker Compose (optional, for containerized setup)

### Local Setup (without Docker)

**1. Clone the repository**

```bash
git clone https://github.com/Mangesh9i7/RAG-Based-Customer-Support-Assistant.git
cd RAG-Based-Customer-Support-Assistant
```

**2. Backend setup**

```bash
cd RAG_Backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file inside `RAG_Backend/`:

```env
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here
ALLOWED_ORIGIN=http://localhost:5173
```

Add at least one knowledge base document to `RAG_Backend/data/raw/` (see [Adding Your Own Knowledge Base](#adding-your-own-knowledge-base)), then start the API:

```bash
uvicorn src.api:api --reload --port 5000
```

The first request will build the FAISS index automatically if one doesn't already exist in `vector_db/`.

**3. Frontend setup**

In a separate terminal:

```bash
cd client
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

> **Note:** in this dev mode, configure Vite's dev server proxy (or adjust API calls) to point at `http://localhost:5000`, since the frontend and backend run on different ports without nginx in front of them.

### Run with Docker Compose

This is the recommended way to run the full stack locally, exactly as it would run in production.

**1. Add your `.env` file** to `RAG_Backend/` as described above.

**2. Build and start both services:**

```bash
docker compose up --build
```

**3. Open the app:**

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend health check: [http://localhost:5000/health](http://localhost:5000/health)

The frontend container runs nginx, which serves the built React app and transparently proxies `/chat` and `/health` requests to the backend container over the internal Docker network — so the browser only ever talks to one origin, and no CORS configuration is needed for this setup.

## Configuration

All backend configuration is via environment variables (`RAG_Backend/.env`):

| Variable         | Required | Description                                                                                         |
| ---------------- | -------- | --------------------------------------------------------------------------------------------------- |
| `GROQ_API_KEY`   | Yes      | API key for Groq, used to call the `llama-3.1-8b-instant` model.                                    |
| `HF_TOKEN`       | Yes      | Hugging Face access token, used for the embeddings Inference API call.                              |
| `ALLOWED_ORIGIN` | No       | CORS-allowed origin for the backend. Defaults to `*` — set explicitly in any non-local environment. |

Retrieval and model behavior are configured in `RAG_Backend/src/config.py`:

| Setting                | Default                | Description                                                                 |
| ---------------------- | ---------------------- | --------------------------------------------------------------------------- |
| `RETRIEVER_K`          | `3`                    | Number of chunks retrieved per query.                                       |
| `GROQ_MODEL_NAME`      | `llama-3.1-8b-instant` | LLM used for generation.                                                    |
| `EMBEDDING_MODEL_NAME` | `all-MiniLM-L6-v2`     | Sentence-transformers model used for embeddings.                            |
| Chunk size / overlap   | `1000` / `150`         | Set in `src/ingestr.py`, controls how documents are split before embedding. |

## How It Works

The core pipeline (`src/graph.py`) is built as a LangChain Expression Language (LCEL) chain:

```python
app = (
    {"context": RunnableLambda(retrieve_and_format), "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)
```

The prompt (`src/prompts.py`) instructs the model to internally classify each question into one of three situations before answering:

1. **Casual chat** (greetings, thanks, small talk) → respond naturally, no document lookup implied.
2. **Context answers the question** → answer directly and helpfully using only the retrieved context.
3. **Context does not answer the question** → return one fixed, verbatim hand-off sentence and nothing else — this is the human-in-the-loop trigger.

This keeps hallucination-avoidance inside the prompt design itself rather than requiring a separate intent-classification model, which keeps the system simple while still giving predictable, auditable behavior for the "don't know the answer" case.

## API Reference

### `POST /chat`

Streams a response to a user question.

**Request body:**

```json
{
  "question": "How do I cancel my order?"
}
```

**Response:** `text/plain`, streamed in chunks as the model generates tokens.

### `GET /health`

Simple liveness check.

**Response:**

```json
{ "status": "ok" }
```

## Adding Your Own Knowledge Base

Drop a single supported file into `RAG_Backend/data/raw/`:

- `.pdf`
- `.txt`
- `.docx` / `.doc`
- `.csv`

The backend automatically picks up the first supported file it finds — no filename or config changes needed. On first run (or after deleting `RAG_Backend/vector_db/`), it will chunk the document, embed it, and build a fresh FAISS index.

> To rebuild the index after updating your knowledge base, delete the contents of `RAG_Backend/vector_db/` and restart the backend — it will regenerate the index automatically on the next request.

## Deployment

Two deployment paths are supported out of the box:

- **`docker-compose.yml`** — frontend and backend as separate containers, nginx reverse proxy in front. Best for local development and any environment where you control container orchestration (VPS, Docker Swarm, Kubernetes with adaptation).
- **Root `Dockerfile`** — a single combined image that builds the React app and serves it directly from FastAPI on port `7860`. Designed for platforms that expect one Dockerfile at the repo root and a single exposed port, such as Hugging Face Spaces.

Use whichever matches your target platform — they are independent of each other and not meant to be used together.

## Known Limitations

- **No conversation memory** — each request is stateless; the model does not see prior turns in the conversation.
- **Chat history is client-side only** — stored in the browser's `localStorage`, so it does not persist across devices or survive clearing browser data.
- **No authentication or rate limiting** on the `/chat` endpoint by default — add this before exposing the API publicly, since every request calls a paid LLM API.
- **Single-document knowledge base** — the ingestion logic picks up the _first_ supported file in `data/raw/`; it is not designed to merge multiple source documents automatically.
- **No automated tests or CI** are currently included.

## Roadmap

- [ ] Conversation memory across turns
- [ ] Server-side chat history persistence
- [ ] Authentication and rate limiting on the API
- [ ] Admin endpoint to trigger re-indexing without manual file deletion
- [ ] Automated tests and CI pipeline
- [ ] Hybrid retrieval (keyword + vector) for better recall on exact terms like order numbers or error codes
