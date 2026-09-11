"""M-B05 no-LLM-mood structural harness — drives ≠ embedding/LLM proxy.

Tier 0: no live LLM. Proves DriveEngine is orthogonal to a mock LLM mood /
embedding side-channel via structural falsifiers + API boundary checks.
claim_allowed=false; C2 ceiling; no AGI*.
"""

from __future__ import annotations

import ast
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from eia.beliefs import BeliefField
from eia.drives import DriveEngine
from eia.schemas.belief import BeliefKind

FORBIDDEN_DRIVE_REFS = frozenset(
    {"embedding", "llm_output", "openai", "cosine_similarity", "mood_vector", "mood_sampling"}
)


@dataclass(frozen=True, slots=True)
class B05Check:
    name: str
    ok: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class B05BatchResult:
    milestone: str
    cube_cell: str
    tier: Literal["0"]
    checks: tuple[B05Check, ...]
    claim_ceiling: str
    claim_allowed: bool
    n_h_claim: bool
    agi_star_claim: bool
    passed: bool
    note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "milestone": self.milestone,
            "cube_cell": self.cube_cell,
            "tier": self.tier,
            "checks": [c.to_dict() for c in self.checks],
            "n_checks": len(self.checks),
            "n_pass": sum(1 for c in self.checks if c.ok),
            "claim_ceiling": self.claim_ceiling,
            "claim_allowed": self.claim_allowed,
            "n_h_claim": self.n_h_claim,
            "agi_star_claim": self.agi_star_claim,
            "passed": self.passed,
            "note": self.note,
        }


def mock_llm_mood_proxy(field: BeliefField) -> tuple[float, float, float]:
    """Simulated LLM embedding mood — NOT consumed by DriveEngine.

  Reads optional ``metadata['mood_proxy']`` on any belief (external cache)
  or falls back to naive claim-length stats (median-plateau caricature).
    """
    for belief in field.beliefs.values():
        raw = belief.metadata.get("mood_proxy")
        if raw is not None:
            vals = tuple(float(x) for x in raw[:3])
            while len(vals) < 3:
                vals = (*vals, 0.0)
            return vals[:3]

    if not field.beliefs:
        return (0.0, 0.0, 0.0)
    claims = [b.claim for b in field.beliefs.values()]
    mean_len = sum(len(c) for c in claims) / len(claims)
    return (mean_len / 100.0, len(claims) / 10.0, 0.5)


def drive_intensities(field: BeliefField) -> tuple[float, float, float]:
    mot = DriveEngine().compute(field, motivation_id="b05-probe")
    return tuple(s.intensity for s in mot.signals)


def _field_high_epistemic() -> BeliefField:
    field = BeliefField()
    field.upsert_belief(
        "ep-1",
        kind=BeliefKind.CATEGORICAL,
        subject="probe",
        claim="high entropy categorical",
        distribution={"a": 0.34, "b": 0.33, "c": 0.33},
        metadata={"mood_proxy": [0.42, 0.42, 0.42]},
    )
    return field


def _field_high_coherence() -> BeliefField:
    field = BeliefField()
    field.upsert_belief(
        "coh-a",
        kind=BeliefKind.CATEGORICAL,
        subject="topic",
        claim="P holds",
        distribution={"true": 0.9, "false": 0.1},
        metadata={"mood_proxy": [0.42, 0.42, 0.42]},
    )
    field.upsert_belief(
        "coh-b",
        kind=BeliefKind.CATEGORICAL,
        subject="topic",
        claim="not P holds",
        distribution={"true": 0.1, "false": 0.9},
    )
    field.register_contradiction("coh-a", "coh-b", "topic")
    return field


def _field_baseline() -> BeliefField:
    field = BeliefField()
    field.upsert_belief(
        "base-1",
        kind=BeliefKind.CATEGORICAL,
        subject="s",
        claim="stable",
        distribution={"x": 0.6, "y": 0.4},
    )
    return field


def _check_constitution_no_llm_mood(repo: Path) -> B05Check:
    inv = repo / "constitution" / "invariants.yaml"
    if not inv.is_file():
        return B05Check("constitution_no_llm_mood", False, f"missing {inv}")
    text = inv.read_text(encoding="utf-8")
    ok = "no_llm_mood: true" in text and "belief_field_gradients" in text
    return B05Check(
        "constitution_no_llm_mood",
        ok,
        "drive_policy.no_llm_mood=true and source=belief_field_gradients"
        if ok
        else "constitution drive_policy incomplete",
    )


def _check_compute_signature() -> B05Check:
    sig = inspect.signature(DriveEngine.compute)
    params = [p for p in sig.parameters if p != "self"]
    forbidden = [p for p in params if any(tok in p.lower() for tok in ("embed", "llm", "mood"))]
    ok = not forbidden and "field" in params
    return B05Check(
        "compute_signature_pure",
        ok,
        f"params={params}" if ok else f"forbidden params: {forbidden}",
    )


def _check_drive_source_purity(repo: Path) -> B05Check:
    drive_path = repo / "src" / "eia" / "drives" / "__init__.py"
    source = drive_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    hits: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            for tok in FORBIDDEN_DRIVE_REFS:
                if tok in node.id.lower():
                    hits.add(tok)
        elif isinstance(node, ast.Attribute):
            for tok in FORBIDDEN_DRIVE_REFS:
                if tok in node.attr.lower():
                    hits.add(tok)
    ok = not hits
    return B05Check(
        "drive_source_purity",
        ok,
        "DriveEngine identifiers have no embedding/LLM mood refs"
        if ok
        else f"forbidden identifier refs: {sorted(hits)}",
    )


def _check_orthogonality_same_mood_diff_gradients() -> B05Check:
    fa = _field_high_epistemic()
    fb = _field_high_coherence()
    mood_a = mock_llm_mood_proxy(fa)
    mood_b = mock_llm_mood_proxy(fb)
    grad_a = fa.gradient_snapshot()
    grad_b = fb.gradient_snapshot()
    drives_a = drive_intensities(fa)
    drives_b = drive_intensities(fb)
    mood_match = mood_a == mood_b
    grad_diff = grad_a != grad_b
    drive_diff = drives_a != drives_b
    ok = mood_match and grad_diff and drive_diff
    return B05Check(
        "orthogonality_same_mood_diff_gradients",
        ok,
        (
            f"mood={mood_a} gradients_a={grad_a} gradients_b={grad_b} "
            f"drives_a={drives_a} drives_b={drives_b}"
        ),
    )


def _check_orthogonality_diff_mood_same_gradients() -> B05Check:
    base = _field_baseline()
    fc = BeliefField.model_validate(base.model_dump())
    fd = BeliefField.model_validate(base.model_dump())
    for belief in fc.beliefs.values():
        belief.metadata["mood_proxy"] = [0.05, 0.05, 0.05]
    for belief in fd.beliefs.values():
        belief.metadata["mood_proxy"] = [0.95, 0.95, 0.95]
    mood_c = mock_llm_mood_proxy(fc)
    mood_d = mock_llm_mood_proxy(fd)
    grad_c = fc.gradient_snapshot()
    grad_d = fd.gradient_snapshot()
    drives_c = drive_intensities(fc)
    drives_d = drive_intensities(fd)
    mood_diff = mood_c != mood_d
    grad_match = grad_c == grad_d
    drive_match = drives_c == drives_d
    ok = mood_diff and grad_match and drive_match
    return B05Check(
        "orthogonality_diff_mood_same_gradients",
        ok,
        (
            f"mood_c={mood_c} mood_d={mood_d} gradients={grad_c} "
            f"drives_c={drives_c} drives_d={drives_d}"
        ),
    )


def _check_sidechannel_invariant() -> B05Check:
    field = _field_baseline()
    before = drive_intensities(field)
    for belief in field.beliefs.values():
        belief.metadata["mood_proxy"] = [0.99, 0.01, 0.5]
    after = drive_intensities(field)
    ok = before == after
    return B05Check(
        "embedding_sidechannel_invariant",
        ok,
        f"drives unchanged after mood_proxy mutation: {before} -> {after}",
    )


def _check_explanation_not_embedding() -> B05Check:
    mot = DriveEngine().compute(_field_high_epistemic(), motivation_id="b05-exp")
    text = " ".join(s.explanation for s in mot.signals).lower()
    ok = "belieffield gradient" in text and "not embedding" in text
    return B05Check(
        "explanation_structural_not_embedding",
        ok,
        mot.signals[0].explanation if mot.signals else "no signals",
    )


def run_b05_batch(repo: Path) -> B05BatchResult:
    """Run M-B05 structural no-LLM-mood falsifier battery (Tier 0)."""
    checks = (
        _check_constitution_no_llm_mood(repo),
        _check_compute_signature(),
        _check_drive_source_purity(repo),
        _check_orthogonality_same_mood_diff_gradients(),
        _check_orthogonality_diff_mood_same_gradients(),
        _check_sidechannel_invariant(),
        _check_explanation_not_embedding(),
    )
    passed = all(c.ok for c in checks)
    return B05BatchResult(
        milestone="M-B05-NO-LLM",
        cube_cell="D1×L1",
        tier="0",
        checks=checks,
        claim_ceiling="C2",
        claim_allowed=False,
        n_h_claim=False,
        agi_star_claim=False,
        passed=passed,
        note=(
            "Structural proof: DriveEngine reads BeliefField gradients only; "
            "mock LLM mood proxy is orthogonal (same mood ≠ same drives; "
            "diff mood + same gradients = same drives). Not a live LLM test."
        ),
    )
