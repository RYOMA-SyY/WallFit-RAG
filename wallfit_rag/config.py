"""Environment-driven settings for Wallfit RAG."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


def _env_bool(key: str, default: str = "1") -> bool:
    return os.environ.get(key, default).strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    # Performance
    stream_delay: float = float(os.getenv("WALLFIT_STREAM_DELAY", "0.01"))
    message_delay: float = float(os.getenv("WALLFIT_MESSAGE_DELAY", "1.5"))
    chroma_persist_dir: str = field(
        default_factory=lambda: os.environ.get("WALLFIT_CHROMA_DIR", "./chroma_db")
    )
    model_id: str = field(
        default_factory=lambda: os.environ.get("WALLFIT_MODEL_ID", "Qwen/Qwen3-8B")
    )
    embed_model: str = field(
        default_factory=lambda: os.environ.get(
            "WALLFIT_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
    )
    embed_device: str = field(
        default_factory=lambda: os.environ.get("WALLFIT_EMBED_DEVICE", "cpu")
    )

    chunk_size: int = int(os.environ.get("WALLFIT_CHUNK_SIZE", "2800"))
    chunk_overlap: int = int(os.environ.get("WALLFIT_CHUNK_OVERLAP", "400"))
    initial_retrieval_k: int = int(os.environ.get("WALLFIT_INITIAL_RETRIEVAL_K", "40"))
    rerank_model: str = field(
        default_factory=lambda: os.environ.get(
            "WALLFIT_RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )
    )
    rerank_top_n: int = int(os.environ.get("WALLFIT_RERANK_TOP_N", "8"))
    context_char_limit: int = int(os.environ.get("WALLFIT_CONTEXT_CHAR_LIMIT", "6000"))

    max_query_length: int = int(os.environ.get("WALLFIT_MAX_QUERY_LENGTH", "500"))

    generation_backend: str = os.environ.get("WALLFIT_GENERATION_BACKEND", "api").strip().lower()

    max_new_tokens: int = int(os.environ.get("WALLFIT_MAX_NEW_TOKENS", "512"))
    temperature: float = float(os.environ.get("WALLFIT_TEMPERATURE", "0.4"))
    top_p: float = float(os.environ.get("WALLFIT_TOP_P", "0.9"))

    hf_token: str | None = field(
        default_factory=lambda: os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    )

    openai_api_key: str | None = field(
        default_factory=lambda: os.environ.get("OPENROUTER_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("AI-APIkey")
    )
    openai_base_url: str = os.environ.get(
        "OPENAI_BASE_URL", "https://openrouter.ai/api/v1"
    ).rstrip("/")
    openai_model: str = os.environ.get("OPENAI_MODEL", "openrouter/owl-alpha")
