# 🏋️ WallFit RAG — Multilingual Women's Fitness AI Coach

A production-grade **Retrieval-Augmented Generation (RAG)** system that embodies "Coach WahibaFit" — a professional Moroccan fitness coach who speaks **English, French, Arabic, and Darija** with a warm "sister to sister" tone.

The system answers fitness, nutrition, and health questions grounded in a curated knowledge base of medical research, health websites, and structured exercise datasets.

---

## ✨ Features

- **🧠 Hybrid Retrieval** — Dense vector search (ChromaDB + all-MiniLM-L6-v2) combined with BM25 keyword search for high-recall context retrieval
- **🎯 Cross-Encoder Reranking** — ms-marco-MiniLM-L-6-v2 reranker to select the top 4 most relevant passages
- **🔒 Security Layer** — PII masking, prompt injection detection (15 regex patterns), input sanitization
- **🌐 Multilingual** — Full support for English, French, Arabic, and Moroccan Darija
- **⚡ Streaming Responses** — SSE-based streaming with configurable delays for natural chat feel
- **🗣️ Voice Support** — Web Speech API integration in the chat UI (Listen button)
- **📋 Session Management** — In-memory chat history, user context pre-loading, session summarization
- **📊 Evaluation Framework** — Automated testing with 50 test cases across 9 categories (fitness, nutrition, security, language, etc.)

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────┐
│  Input Sanitization  │  ← PII masking, injection detection
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│  Hybrid Retrieval    │
│  ┌───────────────┐  │
│  │ ChromaDB      │  │  Dense vector search (k=15)
│  │ (all-MiniLM)  │  │
│  └───────┬───────┘  │
│  ┌───────────────┐  │
│  │ BM25          │  │  Sparse keyword search
│  └───────┬───────┘  │
│    Merge + Dedup     │
│  ┌───────────────┐  │
│  │ Cross-Encoder  │  │  Rerank top 4
│  │ Reranker      │  │
│  └───────────────┘  │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  LLM Generation      │  ← OpenRouter (owl-alpha) or Qwen3-8B local
│  (stream or batch)   │
└──────────┬──────────┘
           ▼
    SSE Stream / JSON Response
```

---

## 📁 Project Structure

```
├── api/                     # FastAPI REST server
│   ├── main.py              # Endpoints: /v1/query, /health, session management
│   └── templates/index.html # Web chat UI (dark theme, voice, markdown)
├── wallfit_rag/             # Core RAG engine package
│   ├── engine.py            # RAGEngine: retrieval, reranking, generation
│   ├── config.py            # Settings dataclass (env-driven)
│   └── security.py          # Input sanitization & injection defense
├── scripts/                 # Utility scripts
│   ├── index_data.py        # Build Chroma vector store from knowledge base
│   └── evaluate_bot.py      # Automated evaluation with 50 test cases
├── DataSet/                 # Knowledge base
│   ├── Exercices DS/        # Exercise & health CSVs (NHANES, gym tracking)
│   ├── webs/                # Curated health articles (PubMed, Healthline, etc.)
│   └── *.pdf                # Research papers (harvard, ijerph, mcPHASES, nihms)
├── chroma_db/               # Persistent vector database (SQLite-backed ChromaDB)
│   └── chroma.sqlite3
├── Evaluation/              # Evaluation reports & test cases
├── logs/                    # LLM telemetry (token usage, latency)
├── WallfitAI RAG COLAB/     # Original Colab notebook + standalone script
├── scratch/                 # Document generation utilities
└── .env                     # Environment configuration
```

---

## 🚀 Quick Start

### 1. Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env` and set your OpenRouter API key:

```
OPENROUTER_API_KEY=sk-or-v1-...
OPENAI_MODEL=openrouter/owl-alpha
```

### 3. Index the Knowledge Base

```bash
python scripts/index_data.py
```

This builds the ChromaDB vector store + BM25 cache from all files in `DataSet/`.

### 4. Start the Server

```bash
uvicorn api.main:app --reload --port 8000
```

Open http://localhost:8000 for the chat UI.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Engine & generator status |
| POST | `/v1/query` | Main query (returns SSE stream) |
| POST | `/v1/user/context` | Pre-load user profile |
| POST | `/v1/session/summarize` | Extract structured summary |
| POST | `/v1/metrics/extract` | Extract numerical metrics |
| POST | `/v1/generate/structured-plan` | Generate workout plan JSON |

---

## 🧪 Evaluation

```bash
python scripts/evaluate_bot.py
```

Runs 50 test cases across 9 categories and generates a markdown report. Latest scores: **4.42–4.47/5**.

---

## 🧠 Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | FastAPI + Uvicorn |
| **Vector DB** | ChromaDB (all-MiniLM-L6-v2 embeddings) |
| **Keyword Search** | BM25 (rank_bm25) |
| **Reranking** | Cross-Encoder (ms-marco-MiniLM-L-6-v2) |
| **LLM** | OpenRouter (owl-alpha) or Qwen3-8B (4-bit quantized) |
| **Security** | Custom PII masking + regex injection detection |
| **UI** | HTML/CSS/JS (Web Speech API, Markdown rendering) |
| **Data** | Pandas, PyPDF, python-docx, HuggingFace Datasets |

---

## 📝 License

This project is developed as part of an internship at **WahibaFit**.
