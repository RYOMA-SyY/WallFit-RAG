# WahibaFit: Expert RAG System for Women's Fitness

WahibaFit is a production-grade Retrieval-Augmented Generation (RAG) assistant designed specifically for women's fitness, nutrition, and health coaching. It combines high-accuracy medical and fitness research with a culturally empathetic, expert persona.

## 🧠 System Overview

The system uses a **Hybrid Retrieval Pipeline** to provide grounded, evidence-based advice through the voice of **Coach WahibaFit**.

### Core Architecture
1.  **Hybrid Search**: Combines dense vector retrieval (ChromaDB) with sparse keyword search (BM25) to capture both semantic meaning and specific terminology.
2.  **Reranking**: A Cross-Encoder reranker (`cross-encoder/ms-marco-MiniLM-L-6-v2`) evaluates the top candidates to ensure the most relevant context is passed to the LLM.
3.  **Knowledge Base**: Curated from medical research PDFs, exercise datasets, and specialized health websites.
4.  **Security Layer**: Multi-step sanitization including PII masking (emails, phone, cards) and robust prompt injection filtering.
5.  **Generation**: Optimized for OpenRouter's `owl-alpha` model for high-reasoning output with low latency.

---

## 🎙️ Persona: Coach WahibaFit

WahibaFit is a professional Moroccan fitness coach. She talks to her clients "sister to sister" with **Saraha Energy** (direct, honest, and expert).

*   **Multilingual**: Native support for English, French, Arabic, and Moroccan Darija.
*   **Mirroring**: Responds in the same language mix used by the user.
*   **Tone**: Authoritative yet empathetic; professional yet sisterly.
*   **Desk-Job Optimization**: Specialized advice for sedentary professionals (standing desks, mobility breaks, walking meetings).

---

## 🎙️ Voice Support

The web interface includes a "Listen" button for AI responses in **English** or **French**. 
*   Uses the browser's native **Web Speech API**.
*   Features a "pulse" animation during playback.

---

## 🔌 API Reference

### 1. Query Endpoint
**`POST /v1/query`**

Primary endpoint for AI interaction. Supports Server-Sent Events (SSE) for streaming.

**Request Body:**
```json
{
  "query": "ma belle, I weigh 70kg and I want to start with something light for my back. what do you suggest?",
  "session_id": "user_session_abc",
  "user_context": {
    "name": "Sarah",
    "goal": "lose 5kg and build core strength"
  }
}
```

**Streamed Response Example:**
```text
data: {"token": "ma"}
data: {"token": " belle"}
...
data: [DONE]
```

---

### 2. Laravel Integration Endpoints

These endpoints are used for synchronization between the AI engine and the Laravel backend.

#### **A. User Context Sync**
**`POST /v1/user/context`**
Pre-loads user profile data from Laravel into a session.

*   **Request**: `{"session_id": "abc", "user_context": {"injuries": "lower back pain"}}`
*   **Response**: `{"status": "success", "message": "Context updated"}`

#### **B. Session Summarization**
**`POST /v1/session/summarize`**
Extracts structured intelligence at the end of a session.

*   **Response**:
```json
{
  "primary_goal": "Start a light fitness routine focused on lower back strengthening",
  "limitations": ["Lower back issues"],
  "preferences": ["Home-based", "Bodyweight", "Light weights"],
  "action_items": ["Perform bridge (3x12)", "Perform side plank (20s)"],
  "sentiment": "motivated"
}
```

#### **C. Metrics Extraction**
**`POST /v1/metrics/extract`**
Extracts numerical data for Laravel database tracking.

*   **Response**: `{"weight_kg": 70}`

#### **D. Structured Plan Generation**
**`POST /v1/generate/structured-plan`**
Converts advice into a renderable UI component (workout card).

*   **Response**:
```json
{
  "plan_name": "Light Back-Focused Home Workout",
  "exercises": [
    {"name": "Bridge", "sets": 3, "reps": 12, "notes": "Controlled movement"}
  ]
}
```

### 3. Utility Endpoints
*   **`GET /health`**: Returns status of the engine and LLM backend.
    *   **Response**: `{"status": "ok", "generator_ready": true}`
*   **`GET /`**: Serves the interactive web test interface for developers.

---

## 🌍 Multilingual Usage Examples

WahibaFit is optimized to detect and mirror the user's language and cultural context.

| Language | User Query | Coach WahibaFit Style |
| :--- | :--- | :--- |
| **English** | "How to stay active with a 9-5 job?" | Direct, science-based, sisterly advice. |
| **French** | "Quels sont les bienfaits du gainage ?" | Professional and encouraging ("ma belle"). |
| **Arabic** | "ما هي أفضل التمارين للمبتدئين؟" | Expert advice using standard Arabic. |
| **Darija** | "bghit nbd ntrini f dar, bchnu nbd?" | Casual, warm, and culturally authentic. |

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `WALLFIT_CHROMA_DIR` | Path to the vector database | `./chroma_db` |
| `OPENROUTER_API_KEY` | OpenRouter API Key | - |
| `OPENAI_MODEL` | LLM Model Identifier | `openrouter/owl-alpha` |
| `WALLFIT_GENERATION_BACKEND` | `api` or `local` | `api` |

---

## 🛠️ Developer Commands

**1. Setup Environment**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**2. Data Indexing**
Builds the vector database and pre-calculates BM25 shards.
```powershell
$env:PYTHONPATH="."; python scripts/index_data.py
```

**3. Start Server**
```powershell
$env:PYTHONPATH="."; python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**4. Stop Server**
```powershell
.\scripts\shutdown_server.ps1
```

---

## 🔒 Security & Privacy
*   **Sanitization**: All inputs are scrubbed of injection attempts before processing.
*   **Anonymization**: PII is masked using regex-based filters before data is indexed or sent to the LLM.
*   **Content Filtering**: Strict enforcement of women's fitness and health scope.

---

## 🚀 Scaling to 1,000+ Concurrent Users

To transition from a development environment to a high-concurrency production setup, follow these architectural recommendations:

### 1. Production Server (Gunicorn)
Do not use `uvicorn` directly in production. Use **Gunicorn** with the Uvicorn worker class to utilize multiple CPU cores.
```bash
# Example: 4 workers for a 4-core machine
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:8000
```

### 2. Session Management (Redis)
Replace the in-memory `SessionManager` in `api/main.py` with **Redis**.
*   **Why**: Enables horizontal scaling (multiple API instances) and prevents session loss during server restarts.
*   **Action**: Update `SessionManager` to use a Redis client for storing chat history and user context.

### 3. GPU Acceleration for Reranking
At scale, the Cross-Encoder reranker can become a bottleneck on CPU.
*   **Requirement**: Use an NVIDIA GPU (T4/L4 or better).
*   **Config**: Ensure `WALLFIT_EMBED_DEVICE` and the Cross-Encoder are mapped to `cuda`.

### 4. Background Processing (Laravel)
The `summarize_session` and `extract_metrics` endpoints involve complex LLM tasks.
*   **Recommendation**: Use **Laravel Queues** (Redis or Database driver) to call these endpoints asynchronously.
*   **Result**: The Flutter app remains responsive while the AI processes the session summary in the background.

### 5. Infrastructure Checklist
| Component | Minimum for 1,000 Users |
| :--- | :--- |
| **RAM** | 16GB - 32GB |
| **CPU** | 8+ vCPUs |
| **GPU** | NVIDIA T4 (16GB VRAM) |
| **Network** | Nginx Reverse Proxy with SSL termination |
