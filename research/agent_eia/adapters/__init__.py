"""Agent-EIA adapters — LLM proposer layer and Brain-AI bridge for shadow harnesses."""

from .brain_agent_bridge import (
    ARM_CONFIG,
    DEFAULT_CONNECTOME_SOURCES,
    apply_omega_psi_to_loop,
    build_connectome_omega_context,
    resolve_arm_config,
)
from .mock_llm_proposer import (
    LlmProposerResult,
    MockLlmProposer,
    resolve_llm_backend,
)

__all__ = [
    "ARM_CONFIG",
    "DEFAULT_CONNECTOME_SOURCES",
    "LlmProposerResult",
    "MockLlmProposer",
    "apply_omega_psi_to_loop",
    "build_connectome_omega_context",
    "resolve_arm_config",
    "resolve_llm_backend",
]
