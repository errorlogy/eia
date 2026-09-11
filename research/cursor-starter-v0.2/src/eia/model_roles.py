"""M-CLI model role adapter (Tier 0 stub - no external LLM calls).

Replaceable roles for goal genesis; default path delegates to compose_from_world_state.
ATT evidence remains Python-only when att_evidence.llm_allowed is false.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from .goal_genesis import CATALOG_GOAL_IDS, GoalGenesisRecord, compose_from_world_state


@dataclass(frozen=True, slots=True)
class GoalCandidate:
    """One proposed instrumental goal (non-claiming)."""

    record: GoalGenesisRecord

    @property
    def goal_id(self) -> str:
        return self.record.goal_id


@dataclass(frozen=True, slots=True)
class GoalGenesisState:
    """Inputs for Tier 0 goal genesis (mirrors compose_from_world_state)."""

    seed: int
    catalog_snapshot: Sequence[str]
    epistemic_pressure: float
    goal_separation: float
    top_target_id: str
    top_target_label: str
    self_prior_mismatch: float
    prospective_tension: float
    peak_coherence: float = 0.75
    prompts_applied: int = 0

    def to_compose_kwargs(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "catalog_snapshot": tuple(self.catalog_snapshot),
            "epistemic_pressure": self.epistemic_pressure,
            "goal_separation": self.goal_separation,
            "top_target_id": self.top_target_id,
            "top_target_label": self.top_target_label,
            "self_prior_mismatch": self.self_prior_mismatch,
            "prospective_tension": self.prospective_tension,
            "peak_coherence": self.peak_coherence,
            "prompts_applied": self.prompts_applied,
        }


@dataclass(frozen=True, slots=True)
class ModelRoleConfig:
    enabled: bool = False
    tier: int = 0
    att_evidence_llm_allowed: bool = False
    goal_genesis_fallback: str = "code"
    goal_genesis_trigger: str = "drive_birth"
    goal_genesis_min_epistemic_pressure: float = 0.35

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> ModelRoleConfig:
        if not data:
            return cls()
        att = data.get("att_evidence") or {}
        genesis = data.get("goal_genesis") or {}
        return cls(
            enabled=bool(data.get("enabled", False)),
            tier=int(data.get("tier", 0)),
            att_evidence_llm_allowed=bool(att.get("llm_allowed", False)),
            goal_genesis_fallback=str(genesis.get("fallback", "code")),
            goal_genesis_trigger=str(genesis.get("trigger", "drive_birth")),
            goal_genesis_min_epistemic_pressure=float(
                genesis.get("min_epistemic_pressure", 0.35)
            ),
        )

    @classmethod
    def from_yaml_file(cls, path: Path) -> ModelRoleConfig:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        section = raw.get("model_roles") or {}
        return cls.from_mapping(section)


class ModelRoleAdapter:
    """Tier 0 adapter: code-only goal candidates."""

    def __init__(self, config: ModelRoleConfig) -> None:
        self.config = config
        if config.att_evidence_llm_allowed and config.tier == 0:
            raise ValueError("tier 0 forbids att_evidence.llm_allowed")

    def propose_goal_candidates(self, state: GoalGenesisState) -> list[GoalCandidate]:
        if self.config.tier != 0:
            raise NotImplementedError(f"model tier {self.config.tier} not implemented")
        if self.config.goal_genesis_fallback != "code":
            raise NotImplementedError(
                f"goal_genesis.fallback={self.config.goal_genesis_fallback!r} not implemented"
            )
        record = compose_from_world_state(**state.to_compose_kwargs())
        return [GoalCandidate(record=record)]

    def genesis_record(self, state: GoalGenesisState) -> GoalGenesisRecord:
        candidates = self.propose_goal_candidates(state)
        return candidates[0].record


def load_model_role_config(path: Path | None = None) -> ModelRoleConfig:
    if path is None:
        repo = Path(__file__).resolve().parents[4]
        path = repo / "research" / "sci_flow" / "config.yaml"
    if not path.is_file():
        return ModelRoleConfig()
    return ModelRoleConfig.from_yaml_file(path)


def maybe_model_role_adapter(path: Path | None = None) -> ModelRoleAdapter | None:
    cfg = load_model_role_config(path)
    if not cfg.enabled:
        return None
    return ModelRoleAdapter(cfg)


def default_catalog_snapshot() -> tuple[str, ...]:
    return tuple(CATALOG_GOAL_IDS)
