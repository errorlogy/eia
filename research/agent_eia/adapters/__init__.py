"""Agent-EIA adapters — LLM proposer layer for shadow harnesses."""

from .mock_llm_proposer import (
    LlmProposerResult,
    MockLlmProposer,
    resolve_llm_backend,
)

__all__ = [
    "LlmProposerResult",
    "MockLlmProposer",
    "resolve_llm_backend",
]
