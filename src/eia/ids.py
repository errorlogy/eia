"""Deterministic ID generation for seeded replay."""

from __future__ import annotations

import contextvars
import hashlib
import uuid
from contextlib import contextmanager
from typing import Iterator

_id_factory: contextvars.ContextVar["IdFactory | None"] = contextvars.ContextVar(
    "id_factory", default=None
)


class IdFactory:
    """Seed-based deterministic IDs — same seed yields same ID sequence."""

    def __init__(self, seed: int) -> None:
        self._seed = seed
        self._counter = 0

    def next(self, prefix: str) -> str:
        self._counter += 1
        digest = hashlib.sha256(
            f"{self._seed}:{prefix}:{self._counter}".encode()
        ).hexdigest()[:8]
        return f"{prefix}-{digest}"


def new_id(prefix: str) -> str:
    """Return a deterministic ID when inside seeded_context, else random."""
    factory = _id_factory.get()
    if factory is not None:
        return factory.next(prefix)
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def new_trace_id(seed: int | None = None) -> str:
    """Deterministic trace id from seed, or random when unseeded."""
    if seed is not None:
        digest = hashlib.sha256(f"trace:{seed}:0".encode()).hexdigest()[:12]
        return f"trace-{digest}"
    return f"trace-{uuid.uuid4().hex[:12]}"


@contextmanager
def seeded_context(seed: int) -> Iterator[IdFactory]:
    """Activate deterministic ID generation for the current context."""
    factory = IdFactory(seed)
    token = _id_factory.set(factory)
    try:
        yield factory
    finally:
        _id_factory.reset(token)
