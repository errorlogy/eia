"""Minimal HDC/VSA episodic binding — Tier C memory adjunct (not proto-AGI).

Bipolar hypervectors with bind=bundle via element-wise multiply and normalized sum.
Deterministic given seed; no external model dependency.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import Any


def _hash_seed(text: str, base_seed: int) -> int:
    digest = hashlib.sha256(f"{base_seed}:{text}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _random_bipolar(dim: int, seed: int) -> list[float]:
    rng_seed = seed
    out: list[float] = []
    for i in range(dim):
        rng_seed = (rng_seed * 1103515245 + 12345 + i) & 0x7FFFFFFF
        out.append(1.0 if (rng_seed % 2) == 0 else -1.0)
    return out


def _normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm <= 1e-12:
        return vec
    return [v / norm for v in vec]


def bind(a: list[float], b: list[float]) -> list[float]:
    return [x * y for x, y in zip(a, b, strict=True)]


def bundle(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        raise ValueError("bundle requires at least one vector")
    dim = len(vectors[0])
    acc = [0.0] * dim
    for vec in vectors:
        for i, v in enumerate(vec):
            acc[i] += v
    return _normalize(acc)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na <= 1e-12 or nb <= 1e-12:
        return 0.0
    return max(-1.0, min(1.0, dot / (na * nb)))


@dataclass
class HDCEpisodicMemory:
    """Episodic key-value store using hypervector binding."""

    dim: int = 512
    seed: int = 42
    similarity_threshold: float = 0.15
    _symbol_cache: dict[str, list[float]] = field(default_factory=dict, repr=False)
    _entries: list[dict[str, Any]] = field(default_factory=list, repr=False)
    _store_hits: int = 0
    _query_hits: int = 0
    _query_misses: int = 0

    def symbol_vector(self, symbol: str) -> list[float]:
        if symbol not in self._symbol_cache:
            self._symbol_cache[symbol] = _random_bipolar(self.dim, _hash_seed(symbol, self.seed))
        return self._symbol_cache[symbol]

    def encode_pair(self, key: str, value: str) -> list[float]:
        key_h = self.symbol_vector(f"KEY:{key}")
        val_h = self.symbol_vector(f"VAL:{value}")
        return bind(key_h, val_h)

    def store(self, key: str, value: str, *, tick: int, metadata: dict[str, Any] | None = None) -> None:
        bound = self.encode_pair(key, value)
        self._entries.append(
            {
                "key": key,
                "value": value,
                "tick": tick,
                "bound": bound,
                "metadata": metadata or {},
            }
        )
        self._store_hits += 1

    def query(self, key: str) -> dict[str, Any]:
        if not self._entries:
            self._query_misses += 1
            return {"hit": False, "key": key, "value": None, "similarity": 0.0}

        probe = self.symbol_vector(f"KEY:{key}")
        for entry in reversed(self._entries):
            if entry["key"] != key:
                continue
            sim = cosine_similarity(probe, self.symbol_vector(f"KEY:{entry['key']}"))
            hit = sim >= self.similarity_threshold
            if hit:
                self._query_hits += 1
            else:
                self._query_misses += 1
            return {
                "hit": hit,
                "key": entry["key"],
                "value": entry["value"],
                "similarity": round(sim, 6),
                "stored_tick": entry["tick"],
                "metadata": entry.get("metadata"),
            }

        self._query_misses += 1
        return {"hit": False, "key": key, "value": None, "similarity": 0.0}

    def stats(self) -> dict[str, Any]:
        total_queries = self._query_hits + self._query_misses
        return {
            "dim": self.dim,
            "entries": len(self._entries),
            "stores": self._store_hits,
            "query_hits": self._query_hits,
            "query_misses": self._query_misses,
            "retrieval_rate": (
                self._query_hits / total_queries if total_queries else 0.0
            ),
        }
