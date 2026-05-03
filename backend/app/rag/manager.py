from __future__ import annotations

import math
import os
import re
from hashlib import sha256
from pathlib import Path
from typing import Iterable

import numpy as np

from app.core.cache import cache
from app.models.mentor import RagSource, RetrievedSnippet
from app.rag.chunking import TextChunk, chunk_markdown

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover - optional runtime dependency can fail on some hosts
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore


SOURCE_LABELS: dict[RagSource, str] = {
    "alumni": "Alumni Knowledge",
    "learning": "Learning Knowledge",
    "job": "Job/Skill Knowledge",
}


class RAGIndex:
    def __init__(self, source: RagSource, chunks: list[TextChunk], model: object | None) -> None:
        self.source = source
        self.chunks = chunks
        self.model = model
        self.index = None
        if faiss is not None and model is not None and chunks:
            embeddings = self._embed([self._search_text(chunk) for chunk in chunks])
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            self.index.add(embeddings)

    def search(self, query: str, top_k: int) -> list[RetrievedSnippet]:
        if self.index is not None and self.model is not None:
            query_embedding = self._embed([query])
            scores, indices = self.index.search(query_embedding, min(top_k, len(self.chunks)))
            results: list[RetrievedSnippet] = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0:
                    continue
                chunk = self.chunks[int(idx)]
                results.append(self._snippet(chunk, float(score)))
            return results
        return self._lexical_search(query, top_k)

    def _embed(self, texts: list[str]) -> np.ndarray:
        assert self.model is not None
        if hasattr(self.model, "encode"):
            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        else:
            embeddings = np.zeros((len(texts), 384), dtype="float32")
        return np.asarray(embeddings, dtype="float32")

    def _lexical_search(self, query: str, top_k: int) -> list[RetrievedSnippet]:
        query_terms = set(re.findall(r"[a-z0-9]+", query.lower()))
        scored: list[tuple[float, TextChunk]] = []
        for chunk in self.chunks:
            terms = set(re.findall(r"[a-z0-9]+", chunk.text.lower()))
            title_terms = set(re.findall(r"[a-z0-9]+", chunk.title.lower()))
            overlap = len(query_terms & terms)
            title_overlap = len(query_terms & title_terms)
            score = (overlap + title_overlap * 2.0) / math.sqrt(max(1, len(terms)))
            scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            self._snippet(chunk, float(score))
            for score, chunk in scored[:top_k]
            if score > 0 or top_k <= 3
        ]

    def _snippet(self, chunk: TextChunk, score: float) -> RetrievedSnippet:
        return RetrievedSnippet(
            source=self.source,
            source_label=SOURCE_LABELS[self.source],
            title=chunk.title,
            text=chunk.text,
            score=score,
            chunk_id=chunk.chunk_id,
            metadata={
                "section_index": chunk.section_index,
                "chunk_index": chunk.chunk_index,
                "retrieval_backend": "faiss" if self.index is not None else "lexical",
            },
        )

    @staticmethod
    def _search_text(chunk: TextChunk) -> str:
        return f"{chunk.title}\n{chunk.text}"


class RAGManager:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.indexes: dict[RagSource, RAGIndex] = {}
        self.ready = False
        self.backend = "lexical"

    def build(self) -> None:
        model = self._load_model()
        self.backend = "faiss" if model is not None and faiss is not None else "lexical"
        for source in ("alumni", "learning", "job"):
            path = self.data_dir / f"{source}.md"
            content = path.read_text(encoding="utf-8") if path.exists() else ""
            chunks = chunk_markdown(source, content)
            self.indexes[source] = RAGIndex(source, chunks, model)
        self.ready = bool(self.indexes)

    def retrieve(self, query: str, sources: Iterable[RagSource], top_k: int = 4) -> list[RetrievedSnippet]:
        source_list = list(sources)
        cache_key = self._cache_key(query, source_list, top_k)
        cached = cache.get(cache_key)
        if isinstance(cached, list):
            return cached

        results: list[RetrievedSnippet] = []
        for source in source_list:
            index = self.indexes.get(source)
            if not index:
                continue
            results.extend(index.search(query, top_k=top_k))
        deduped: dict[str, RetrievedSnippet] = {}
        for result in sorted(results, key=lambda item: item.score, reverse=True):
            deduped.setdefault(result.chunk_id, result)
        output = list(deduped.values())[:top_k]
        cache.set(cache_key, output, ttl_seconds=5 * 60)
        return output

    def route(self, query: str, requested: str | list[RagSource] = "auto") -> list[RagSource]:
        sources, _ = self.route_with_reason(query, requested)
        return sources

    def route_with_reason(self, query: str, requested: str | list[RagSource] = "auto") -> tuple[list[RagSource], str]:
        if requested != "auto":
            sources = list(dict.fromkeys(requested))
            labels = ", ".join(SOURCE_LABELS[source] for source in sources)
            return sources, f"Manual source selection: {labels}."

        lowered = query.lower()
        learning = bool(re.search(r"\b(how|learn|roadmap|tutorial|build|study|practice)\b", lowered))
        job = bool(re.search(r"\b(job|required|role|hiring|expectations|recruiter|interview)\b", lowered))
        if learning and job:
            return ["learning", "job"], "The query mixes learning intent with role expectations, so SkillLens merged Learning and Job/Skill RAG."
        if learning:
            return ["learning"], "Learning RAG was selected because the query asks how to learn, build, study, or follow a roadmap."
        if job:
            return ["job"], "Job/Skill RAG was selected because the query asks about required skills, hiring, roles, or interviews."
        if "compare" in lowered or "gap" in lowered:
            return ["alumni", "learning", "job"], "Gap language benefits from career advice, learning steps, and role expectations, so all three RAG sources were merged."
        return ["alumni"], "Alumni RAG was selected for general career guidance and experience-based advice."

    @staticmethod
    def _load_model() -> object | None:
        if os.getenv("ENABLE_SEMANTIC_RAG", "").lower() not in {"1", "true", "yes"}:
            return None
        if SentenceTransformer is None or faiss is None:
            return None
        try:
            return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        except Exception:
            return None

    @staticmethod
    def _cache_key(query: str, sources: list[RagSource], top_k: int) -> str:
        raw = f"{query.lower().strip()}|{','.join(sources)}|{top_k}"
        return f"rag:{sha256(raw.encode('utf-8')).hexdigest()}"
