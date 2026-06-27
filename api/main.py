"""
WahibaFit API — Clean version with external template.
"""

import os
import json
import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from pydantic import BaseModel

from wallfit_rag.config import Settings
from wallfit_rag.engine import RAGEngine

_engine: RAGEngine | None = None

class SessionManager:
    """Simple in-memory storage for chat history and user context."""
    def __init__(self, max_history: int = 10):
        self.sessions: dict[str, list[dict[str, str]]] = {}
        self.contexts: dict[str, dict] = {}
        self.max_history = max_history

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        return self.sessions.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": role, "content": content})
        if len(self.sessions[session_id]) > self.max_history:
            self.sessions[session_id] = self.sessions[session_id][-self.max_history:]

    def set_context(self, session_id: str, context: dict):
        self.contexts[session_id] = context

    def get_context(self, session_id: str) -> dict | None:
        return self.contexts.get(session_id)

memory = SessionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _engine
    settings = Settings()
    _engine = RAGEngine(settings)
    _engine.load_vector_store()
    if os.environ.get("WALLFIT_SKIP_LLM", "").strip().lower() not in ("1", "true"):
        _engine.load_generator()
    yield
    _engine = None

app = FastAPI(title="WahibaFit API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    session_id: str = "default"
    user_context: dict | None = None

class ContextRequest(BaseModel):
    session_id: str
    user_context: dict

class SessionSummaryRequest(BaseModel):
    session_id: str

@app.get("/health")
def health():
    return {"status": "ok", "generator_ready": _engine.generator_ready if _engine else False}

@app.post("/v1/user/context")
async def set_user_context(body: ContextRequest):
    memory.set_context(body.session_id, body.user_context)
    return {"status": "success", "message": f"Context updated for session {body.session_id}"}

@app.post("/v1/session/summarize")
async def summarize_session(body: SessionSummaryRequest):
    if _engine is None or not _engine.generator_ready:
        raise HTTPException(status_code=503, detail="Engine not ready")
    
    history = memory.get_history(body.session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session history not found")
    
    summary = _engine.summarize_session(history)
    return summary

@app.post("/v1/metrics/extract")
async def extract_metrics(body: SessionSummaryRequest):
    if _engine is None or not _engine.generator_ready:
        raise HTTPException(status_code=503, detail="Engine not ready")
    
    history = memory.get_history(body.session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session history not found")
    
    metrics = _engine.extract_metrics(history)
    return metrics

@app.post("/v1/generate/structured-plan")
async def generate_plan(body: SessionSummaryRequest):
    if _engine is None or not _engine.generator_ready:
        raise HTTPException(status_code=503, detail="Engine not ready")
    
    history = memory.get_history(body.session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session history not found")
    
    plan = _engine.generate_structured_plan(history)
    return plan

@app.post("/v1/query")
async def query_v1(body: QueryRequest):
    if _engine is None or not _engine.generator_ready:
        raise HTTPException(status_code=503, detail="Engine not ready")

    try:
        # Merge manual context with remembered context
        stored_ctx = memory.get_context(body.session_id) or {}
        active_ctx = {**stored_ctx, **(body.user_context or {})}
        
        history = memory.get_history(body.session_id)
        gen = _engine.ask(body.query, history=history, user_context=active_ctx, stream=True)
        
        async def event_generator():
            full_answer = ""
            try:
                # 1. Initial delay before the first bubble starts
                if _engine and _engine.settings.message_delay > 0:
                    await asyncio.sleep(_engine.settings.message_delay)

                # We iterate the sync generator from the engine
                # FastAPI runs this in a threadpool, but we'll yield carefully
                for chunk in gen:
                    if chunk:
                        # If the chunk contains paragraph breaks, we need to split it 
                        # to ensure the delay is applied between the bubbles.
                        if "\n\n" in chunk:
                            parts = chunk.split("\n\n")
                            for i, part in enumerate(parts):
                                if i > 0:
                                    # We just crossed a \n\n boundary
                                    if _engine and _engine.settings.message_delay > 0:
                                        await asyncio.sleep(_engine.settings.message_delay)
                                
                                # Re-attach the \n\n if it's not the last part
                                # so the frontend knows where to split.
                                current_payload = part + ("\n\n" if i < len(parts) - 1 else "")
                                if current_payload:
                                    full_answer += current_payload
                                    yield f"data: {json.dumps({'token': current_payload})}\n\n"
                                    if _engine and _engine.settings.stream_delay > 0:
                                        await asyncio.sleep(_engine.settings.stream_delay)
                        else:
                            full_answer += chunk
                            yield f"data: {json.dumps({'token': chunk})}\n\n"
                            
                            # Handle standard stream delay
                            if _engine:
                                if full_answer.endswith("\n\n"):
                                    if _engine.settings.message_delay > 0:
                                        await asyncio.sleep(_engine.settings.message_delay)
                                elif _engine.settings.stream_delay > 0:
                                    await asyncio.sleep(_engine.settings.stream_delay)
                
                memory.add_message(body.session_id, "user", body.query)
                memory.add_message(body.session_id, "assistant", full_answer)
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=FileResponse)
def web_tester():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    return FileResponse(template_path)
