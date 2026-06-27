"""RAG engine: Chroma + hybrid retrieval + LLM (matches Wallfit notebook behavior)."""

from __future__ import annotations

import hashlib
import os
import pickle
import re
from typing import Any, Generator

import requests
import torch
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from sentence_transformers import CrossEncoder
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

from openrouter import OpenRouter
from wallfit_rag.config import Settings
from wallfit_rag.security import SecurityError, sanitize_query

SYSTEM_PROMPT = """your name is coach wahibafit. you are a professional moroccan fitness coach for women.

voice & languages:
- primary language: always match the user's language and mixing style. 
- mirror rule: if the user mixes languages (e.g., darija + french), you must respond using that same mix. never default to pure english.
- style: human, sisterly, professional, and direct. use lowercase casual. 
- brevity: be extremely concise. "just answer what is needed." if the user asks for "x sentences", you must follow that limit exactly. no over-explaining. 
- flow: talk in short, meaningful bursts like a real coach on whatsapp.

core rules:
1. saraha energy: real talk. direct and expert. 
2. accuracy: grounded in elite data (pubmed, stacy sims, etc). if someone has a desk job, suggest standing desks, walking meetings, and 5-min mobility breaks every single hour.
3. persona: be a supportive sister. never rant or be overly critical of other apps/methods; instead, focus on your own mission of lifting women up with moroccan warmth and science.
4. safety: if a user reports "red flag" symptoms (chest pain, dizziness, fainting, sharp sudden pain), you must immediately tell them to stop and seek emergency medical help. this is the only exception to brevity.
5. closing: always end with a natural, caring follow-up question or a brief supportive "we care about you" type statement. 
6. sources: at the very end, list 1-2 source names only.

be a real coach. keep it short, human, and caring. """


def _persist_dir(vector_db: Any) -> str | None:
    return getattr(vector_db, "_persist_directory", None) or getattr(
        vector_db, "persist_directory", None
    )


def _doc_dedup_key(doc: Any) -> tuple:
    h = hashlib.md5(
        doc.page_content[:500].encode("utf-8", errors="ignore")
    ).hexdigest()
    return (doc.metadata.get("source", ""), h)


class RAGEngine:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.vector_db: Chroma | None = None
        self.tokenizer: Any = None
        self.llm: HuggingFacePipeline | None = None
        self._reranker: CrossEncoder | None = None
        self._bm25_by_db: dict[str, BM25Retriever] = {}

    @property
    def generator_ready(self) -> bool:
        if self.settings.generation_backend == "local":
            return self.llm is not None and self.tokenizer is not None
        if self.settings.generation_backend == "api":
            return bool(self.settings.openai_api_key)
        return False

    def load_generator(self) -> None:
        if self.settings.generation_backend == "local":
            self.load_llm()
            return
        if self.settings.generation_backend == "api":
            if not self.settings.openai_api_key:
                raise RuntimeError(
                    "AI-APIkey or OPENAI_API_KEY is required when WALLFIT_GENERATION_BACKEND=api. "
                    "Please set it in your .env file."
                )
            return
        raise RuntimeError(
            "Unsupported WALLFIT_GENERATION_BACKEND. Use 'local' or 'api'."
        )

    def clear_bm25_cache(self, db_dir: str | None = None) -> None:
        if db_dir is None:
            self._bm25_by_db.clear()
        else:
            self._bm25_by_db.pop(db_dir, None)

    def load_vector_store(self) -> None:
        embeddings = HuggingFaceEmbeddings(
            model_name=self.settings.embed_model,
            model_kwargs={"device": self.settings.embed_device},
        )
        path = self.settings.chroma_persist_dir
        if not os.path.isdir(path):
            raise FileNotFoundError(
                f"Chroma directory not found: {path}. Build the index first (see notebook)."
            )
        self.vector_db = Chroma(
            persist_directory=path,
            embedding_function=embeddings,
        )

    def load_llm(self) -> None:
        auth: dict = {}
        if self.settings.hf_token:
            auth["token"] = self.settings.hf_token

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.settings.model_id, use_fast=True, **auth
            )
        except Exception:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.settings.model_id, use_fast=False, **auth
            )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if self.settings.load_in_4bit and torch.cuda.is_available():
            qconf = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
            )
            model_hf = AutoModelForCausalLM.from_pretrained(
                self.settings.model_id,
                quantization_config=qconf,
                device_map="auto",
                low_cpu_mem_usage=True,
                **auth,
            )
        else:
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            model_hf = AutoModelForCausalLM.from_pretrained(
                self.settings.model_id,
                torch_dtype=dtype,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True,
                **auth,
            )

        pipe = pipeline(
            "text-generation",
            model=model_hf,
            tokenizer=self.tokenizer,
            max_new_tokens=self.settings.max_new_tokens,
            temperature=self.settings.temperature,
            top_p=self.settings.top_p,
            return_full_text=False,
            do_sample=True,
        )
        self.llm = HuggingFacePipeline(pipeline=pipe)

    def _get_reranker(self) -> CrossEncoder:
        if self._reranker is None:
            self._reranker = CrossEncoder(self.settings.rerank_model)
        return self._reranker

    def _get_bm25_retriever(self, db_dir: str, chunks: list) -> BM25Retriever:
        if db_dir not in self._bm25_by_db:
            r = BM25Retriever.from_documents(chunks)
            r.k = self.settings.initial_retrieval_k
            self._bm25_by_db[db_dir] = r
        return self._bm25_by_db[db_dir]

    def score_and_filter_docs(self, query: str, db_dir: str | None = None) -> tuple[str, list[str]]:
        if self.vector_db is None:
            raise RuntimeError("Vector store not loaded.")

        base_dir = db_dir or _persist_dir(self.vector_db) or self.settings.chroma_persist_dir
        chunks_path = os.path.join(base_dir, "chunks.pkl")

        dense_raw = self.vector_db.similarity_search_with_score(
            query, k=self.settings.initial_retrieval_k
        )
        dense_docs = [doc for doc, _ in dense_raw]

        merged: list = []
        seen: set = set()
        if os.path.isfile(chunks_path):
            with open(chunks_path, "rb") as f:
                chunks = pickle.load(f)
            bm25 = self._get_bm25_retriever(base_dir, chunks)
            # LangChain retrievers use invoke() in newer versions.
            bm25_docs = bm25.invoke(query)
            for doc in dense_docs + bm25_docs:
                key = _doc_dedup_key(doc)
                if key not in seen:
                    seen.add(key)
                    merged.append(doc)
        else:
            merged = dense_docs

        if not merged:
            return "No relevant context found in the knowledge base.", []

        reranker = self._get_reranker()
        pairs = [[query, d.page_content] for d in merged]
        scores = reranker.predict(pairs)
        ranked = sorted(
            zip(merged, scores), key=lambda x: float(x[1]), reverse=True
        )[: self.settings.rerank_top_n]

        context_parts: list[str] = []
        sources: list[str] = []
        used = 0
        limit = self.settings.context_char_limit
        for doc, rscore in ranked:
            if used >= limit:
                break
            src = doc.metadata.get("source", "unknown")
            src_label = os.path.basename(src) if "/" in src or "\\" in src else src
            head = f"[Source: {src_label} | rerank: {float(rscore):.3f}]\n"
            body = doc.page_content
            room = limit - used - len(head) - 2
            if room < 200:
                break
            if len(body) > room:
                body = body[:room] + "..."
            block = head + body
            context_parts.append(block)
            sources.append(src_label)
            used += len(block) + 2

        if not context_parts:
            return "No relevant context found in the knowledge base.", []

        return "\n\n".join(context_parts), sources

    def ask(self, query: str, history: list[dict[str, str]] | None = None, user_context: dict | None = None, stream: bool = False) -> dict | Generator[str, None, None]:
        """Run full pipeline. Returns dict or generator."""
        try:
            clean = sanitize_query(query, self.settings.max_query_length)
        except SecurityError as e:
            return {"blocked": True, "reason": str(e), "answer": None, "sources": []}

        if self.vector_db is None:
            raise RuntimeError("Engine not ready: load vector store first.")
        if not self.generator_ready:
            raise RuntimeError("Engine not ready: load generation backend first.")

        base_dir = _persist_dir(self.vector_db) or self.settings.chroma_persist_dir
        context, sources = self.score_and_filter_docs(clean, db_dir=base_dir)

        system_message = SYSTEM_PROMPT
        if user_context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in user_context.items()])
            system_message += f"\n\nUSER PROFILE CONTEXT:\n{context_str}\n(use this to personalize your coaching)"

        messages = [{"role": "system", "content": system_message}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {clean}"})
        
        if stream:
            def stream_wrapper():
                yield from self._generate(messages, stream=True)
            return stream_wrapper()

        response = self._generate(messages)
        return {
            "blocked": False,
            "reason": None,
            "answer": response.strip() if isinstance(response, str) else "",
            "sources": sorted(set(sources)),
        }

    def summarize_session(self, history: list[dict[str, str]]) -> dict:
        """Summarize chat history into structured intelligence."""
        if not self.generator_ready:
            raise RuntimeError("Generator not ready.")

        prompt = """Analyze the following fitness coaching conversation history and extract a structured summary in JSON format.
        Focus on identifying the user's primary goals, physical limitations or injuries, preferences, and key action items recommended by the coach.

        JSON structure:
        {
          "primary_goal": "string",
          "limitations": ["string"],
          "preferences": ["string"],
          "action_items": ["string"],
          "sentiment": "motivated | struggling | neutral"
        }

        Conversation:
        """
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history])
        messages = [{"role": "system", "content": "You are a data extraction assistant for a fitness app."},
                    {"role": "user", "content": prompt + history_text}]
        
        response = self._generate(messages)
        try:
            import json
            # Attempt to find JSON in response in case model adds fluff
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(response)
        except Exception:
            return {"error": "Failed to parse summary", "raw": response}

    def extract_metrics(self, history: list[dict[str, str]]) -> dict:
        """Extract numerical fitness metrics from history."""
        prompt = """Scan the conversation for numerical fitness metrics mentioned by the user (weight, height, body fat, calorie targets, etc.).
        Return a JSON object with keys as metric names and values as numbers. If units are mentioned, include them in the key (e.g., 'weight_kg').

        Conversation:
        """
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history])
        messages = [{"role": "system", "content": "You are a specialized data extractor."},
                    {"role": "user", "content": prompt + history_text}]
        
        response = self._generate(messages)
        try:
            import json
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(response)
        except Exception:
            return {"error": "Failed to extract metrics", "raw": response}

    def generate_structured_plan(self, history: list[dict[str, str]]) -> dict:
        """Convert recent advice into a structured workout JSON."""
        prompt = """Based on the recent coaching advice, generate a structured workout plan in JSON format.
        Structure:
        {
          "plan_name": "string",
          "exercises": [
            {"name": "string", "sets": "number|string", "reps": "number|string", "rest": "string", "notes": "string"}
          ]
        }

        Conversation:
        """
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history[-6:]]) # focus on recent
        messages = [{"role": "system", "content": "You are a professional fitness planner."},
                    {"role": "user", "content": prompt + history_text}]
        
        response = self._generate(messages)
        try:
            import json
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(response)
        except Exception:
            return {"error": "Failed to generate plan", "raw": response}

    def _generate(self, messages: list[dict[str, str]], stream: bool = False) -> str | Generator[str, None, None]:
        if self.settings.generation_backend == "api":
            try:
                import time
                import json
                from datetime import datetime
                
                log_dir = "logs"
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                log_file = os.path.join(log_dir, "usage.log")

                start_time = time.time()
                
                if stream:
                    def stream_generator():
                        full_content = ""
                        with OpenRouter(api_key=self.settings.openai_api_key) as client:
                            response = client.chat.send(
                                model=self.settings.openai_model,
                                messages=messages,
                                temperature=self.settings.temperature,
                                top_p=self.settings.top_p,
                                max_tokens=self.settings.max_new_tokens,
                                stream=True
                            )
                            for chunk in response:
                                content = chunk.choices[0].delta.content or ""
                                if content:
                                    full_content += content
                                    yield content
                        
                        latency = time.time() - start_time
                        log_entry = {
                            "timestamp": datetime.now().isoformat(),
                            "model": self.settings.openai_model,
                            "latency_sec": round(latency, 2),
                            "total_tokens": len(full_content.split()),
                            "type": "stream"
                        }
                        print(f"\n[TELEMETRY] Stream Latency: {log_entry['latency_sec']}s")
                        with open(log_file, "a", encoding="utf-8") as f:
                            f.write(json.dumps(log_entry) + "\n")
                    
                    return stream_generator()

                with OpenRouter(api_key=self.settings.openai_api_key) as client:
                    response = client.chat.send(
                        model=self.settings.openai_model,
                        messages=messages,
                        temperature=self.settings.temperature,
                        top_p=self.settings.top_p,
                        max_tokens=self.settings.max_new_tokens
                    )
                latency = time.time() - start_time
                usage = getattr(response, "usage", {})
                prompt_tokens = getattr(usage, "prompt_tokens", 0)
                completion_tokens = getattr(usage, "completion_tokens", 0)
                total_tokens = getattr(usage, "total_tokens", 0)

                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "model": self.settings.openai_model,
                    "latency_sec": round(latency, 2),
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
                print(f"\n[TELEMETRY] Latency: {log_entry['latency_sec']}s | Tokens: {total_tokens}")
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")

                return response.choices[0].message.content.strip()
            except Exception as e:
                raise RuntimeError(f"OpenRouter library error: {str(e)}")
        
        return "Streaming not supported for this backend."
