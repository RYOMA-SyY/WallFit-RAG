# WallfitAI Technical Documentation

## Project Overview

WallfitAI is a secure, multilingual Retrieval-Augmented Generation (RAG) system designed as a fitness assistant for women. It uses a **Qwen3 8B** causal model with **4-bit quantization** to produce answers grounded in a custom knowledge base, with **hybrid retrieval** (dense + BM25) and **cross-encoder reranking** to improve which passages reach the model.

## Architecture

### 1. Large Language Model

- **Model:** `Qwen/Qwen3-8B` (configured in the notebook; adjust `MODEL_ID` if you switch checkpoints).
- **Quantization:** 4-bit NF4 via BitsAndBytes.
- **Platform:** Google Colab (T4 GPU typical).
- **Inference:** Hugging Face `transformers` pipeline wrapped with LangChain `HuggingFacePipeline`.
- **Generation defaults (factual RAG):** `temperature≈0.35`, `top_p≈0.88`, `max_new_tokens=512` (see notebook for exact values).

### 2. Retrieval System

- **Vector store:** ChromaDB (`langchain_community.vectorstores.Chroma`).
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (often on **CPU** to preserve GPU VRAM for the LLM).
- **Chunking:** `RecursiveCharacterTextSplitter` with **`CHUNK_SIZE=2800`** and **`CHUNK_OVERLAP=400`** (character-based, sized to approximate medium-to-large context chunks).
- **Hybrid recall:**
  - **Dense:** similarity search over Chroma with **`INITIAL_RETRIEVAL_K`** (e.g. 40).
  - **Sparse:** **BM25** over the same chunk set (`rank_bm25` + LangChain `BM25Retriever`).
- **Chunk cache:** On index build, chunks are saved as **`chunks.pkl`** under the Chroma persist directory so BM25 uses identical splits to the vector index.
- **Reranking:** **`cross-encoder/ms-marco-MiniLM-L-6-v2`** scores merged, deduplicated candidates; top **`RERANK_TOP_N`** chunks contribute to the prompt, bounded by **`CONTEXT_CHAR_LIMIT`** (total context character budget).

Relevant tunables live in the notebook **config** cell (`CHUNK_*`, `INITIAL_RETRIEVAL_K`, `RERANK_*`, `CONTEXT_CHAR_LIMIT`, etc.).

### 3. Data Sources

- **Local files:** PDFs and CSVs on Google Drive, loaded only if the filename is on **`TRUSTED_SOURCES`**.
- **Hugging Face datasets:**

  - `hammamwahab/fitness-qa`
  - `chibbss/fitness-chat-prompt-completion-dataset`
  - `onurSakar/GYM-Exercise`
  - `its-myrto/fitness-question-answers`

## Security Framework

### Input Sanitization

The system uses regex-based checks to block:

- Prompt injection patterns (e.g. “ignore previous instructions”).
- Persona override / jailbreak-style phrasing.
- Requests to leak system or hidden prompts.

Queries exceeding **`MAX_QUERY_LENGTH`** are rejected.

### Data Privacy

- **PII masking** before embedding (emails, phones, card-like patterns, common secret patterns).
- **Trusted ingestion:** only whitelisted local filenames are loaded from Drive.

### Output and Grounding

- **System prompt:** Fixed role as a women’s fitness assistant; multilingual behavior (English, French, Arabic, Darija).
- **Grounding rules:** Instruct the model to rely on **CONTEXT**, avoid inventing unsupported numbers or study claims, and name which source labels from CONTEXT it used.
- **Structured answer guidance:** Bullets where helpful, plus a **Limitations** bullet for when to seek a qualified clinician (injury, pregnancy, chest pain, eating disorders, red flags).
- **Retrieval quality:** Irrelevant passages are reduced via **reranking** and a **context character cap**, not a single fixed L2 distance threshold on the first five hits.

## Multilingual Support

The assistant is expected to **mirror the user’s language**:

- English  
- French  
- Arabic  
- Darija (Moroccan Arabic; match the user’s script when appropriate)

## Deployment Instructions

### Notebook (Colab / research)

1. **Environment:** Open `Wallfit.ipynb`, select a **GPU** runtime.
2. **Dependencies:** Run the install cell (`rank_bm25`, LangChain, Chroma, etc.).
3. **Data:** Mount Drive and set **`DATASET_DIR`** to your dataset folder; keep **`TRUSTED_SOURCES`** in sync with real filenames.
4. **Index:** Run **`build_vector_db`** so Chroma and **`chunks.pkl`** exist under your **`DB_DIR`**.
5. **Model:** Run the LLM cell, then the RAG cell.
6. **Troubleshooting:** OOM → restart runtime or reduce retrieval / model size; missing **`chunks.pkl`** → rebuild the vector DB.

### REST API (FastAPI)

The **`api/`** package exposes a small REST service that uses the same RAG logic as the notebook via **`wallfit_rag.RAGEngine`**.

**Install API extras** (in addition to your existing ML dependencies):

```bash
pip install -r requirements-api.txt
```

**Run** (from the project root `WallfitAI/`):

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Copy the vector index** from Colab (or build locally): point **`WALLFIT_CHROMA_DIR`** at the folder that contains the Chroma SQLite data **and** **`chunks.pkl`** (same directory the notebook uses as `persist_directory`).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Process up; whether Chroma and LLM are loaded |
| `/ready` | GET | Returns 200 only if Chroma + LLM are ready (for probes) |
| `/v1/query` | POST | JSON `{"query": "..."}` → answer + sources |
| `/ask` | POST | Alias of `/v1/query` |

**Response shape** (`POST /v1/query`):

- `answer`: model reply (or `null` if blocked)
- `sources`: list of source labels used in context
- `blocked`: `true` if input failed security checks
- `reason`: short message when blocked

**Useful environment variables** (see `wallfit_rag/config.py` for the full set):

- **`WALLFIT_CHROMA_DIR`** — path to persisted Chroma + `chunks.pkl` (default `./chroma_db`)
- **`WALLFIT_MODEL_ID`** — Hugging Face model id (default `Qwen/Qwen3-8B`)
- **`HF_TOKEN` / `HUGGINGFACE_HUB_TOKEN`** — for gated models
- **`WALLFIT_CORS_ORIGINS`** — comma-separated origins, or `*` (default)
- **`WALLFIT_SKIP_LLM=1`** — start API without loading the LLM (health checks only)

For production, put the API behind HTTPS, rate-limit **`/v1/query`**, and do not expose **`HF_TOKEN`** in client apps.
