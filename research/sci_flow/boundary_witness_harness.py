"""D3×L3 boundary witness harness — N_H soft witness + falsifier smoke (C2 ceiling).

Measures boundary-layer receipts without claiming strong N_H or AGI*.
See research/sci_flow/D3_BOUNDARY_WITNESS.md for scope.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

REQUIRED_BOUNDARY_FALSIFIERS = frozenset({"F-DECL", "F-NARR", "F-EXT", "F-NODO"})
WitnessTier = Literal["B_soft_NH", "B_partial"]


@dataclass(frozen=True, slots=True)
class FalsifierRegistryRow:
    intervention_count_d3: int
    registry_falsifiers: tuple[str, ...]
    causal_doc_falsifiers: tuple[str, ...]
    linked: tuple[str, ...]
    missing: tuple[str, ...]
    ok: bool


@dataclass(frozen=True, slots=True)
class GovernorGateRow:
    deny_low_value: bool
    min_contact_score: float
    cf7_intervention_present: bool
    ok: bool


@dataclass(frozen=True, slots=True)
class AttNBoundaryRow:
    n_seeds: int
    causal_att_n_rate: float | None
    claim_allowed: bool
    n_h_claim: bool
    ok: bool


@dataclass(frozen=True, slots=True)
class NammSoftWitnessRow:
    intent_files: int
    valid_json: int
    domains: tuple[str, ...]
    tier: str
    ok: bool


@dataclass(frozen=True, slots=True)
class BoundaryWitnessResult:
    falsifier_registry: FalsifierRegistryRow
    governor_gate: GovernorGateRow
    att_n: AttNBoundaryRow
    namm_soft: NammSoftWitnessRow
    witness_tier: WitnessTier
    claim_ceiling: str
    claim_allowed: bool
    n_h_claim: bool
    agi_star_claim: bool
    passed: bool
    note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "witness_tier": self.witness_tier,
            "claim_ceiling": self.claim_ceiling,
            "claim_allowed": self.claim_allowed,
            "n_h_claim": self.n_h_claim,
            "agi_star_claim": self.agi_star_claim,
            "passed": self.passed,
            "note": self.note,
            "falsifier_registry": {
                "intervention_count_d3": self.falsifier_registry.intervention_count_d3,
                "registry_falsifiers": list(self.falsifier_registry.registry_falsifiers),
                "causal_doc_falsifiers": list(self.falsifier_registry.causal_doc_falsifiers),
                "linked": list(self.falsifier_registry.linked),
                "missing": list(self.falsifier_registry.missing),
                "ok": self.falsifier_registry.ok,
            },
            "governor_gate": {
                "deny_low_value": self.governor_gate.deny_low_value,
                "min_contact_score": self.governor_gate.min_contact_score,
                "cf7_intervention_present": self.governor_gate.cf7_intervention_present,
                "ok": self.governor_gate.ok,
            },
            "att_n": {
                "n_seeds": self.att_n.n_seeds,
                "causal_att_n_rate": self.att_n.causal_att_n_rate,
                "claim_allowed": self.att_n.claim_allowed,
                "n_h_claim": self.att_n.n_h_claim,
                "ok": self.att_n.ok,
            },
            "namm_soft": {
                "intent_files": self.namm_soft.intent_files,
                "valid_json": self.namm_soft.valid_json,
                "domains": list(self.namm_soft.domains),
                "tier": self.namm_soft.tier,
                "ok": self.namm_soft.ok,
            },
        }


def _load_woe_submodule(repo: Path, name: str) -> Any:
    woe_pkg = repo / "research" / "cursor-starter-v0.2" / "src" / "eia"
    pkg_name = "woe_boundary_witness"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [str(woe_pkg)]  # type: ignore[attr-defined]
        sys.modules[pkg_name] = pkg
    full = f"{pkg_name}.{name}"
    if full in sys.modules:
        return sys.modules[full]
    path = woe_pkg / f"{name}.py"
    spec = importlib.util.spec_from_file_location(full, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = pkg_name
    sys.modules[full] = mod
    spec.loader.exec_module(mod)
    return mod


def _falsifiers_in_doc(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    text = path.read_text(encoding="utf-8")
    return {f for f in REQUIRED_BOUNDARY_FALSIFIERS if f in text}


def run_falsifier_registry_smoke(repo: Path) -> FalsifierRegistryRow:
    intervention_cube = _load_woe_submodule(repo, "intervention_cube")
    d3_items = intervention_cube.list_by_axis("D3")
    registry_fals: set[str] = set()
    for item in intervention_cube.list_all():
        registry_fals.update(item.falsifiers)

    causal_path = repo / "research" / "sci_flow" / "CAUSAL_ENDOGENEITY.md"
    causal_fals = _falsifiers_in_doc(causal_path)
    linked = set(registry_fals) | causal_fals
    missing = sorted(REQUIRED_BOUNDARY_FALSIFIERS - linked)
    ok = len(d3_items) >= 2 and not missing
    return FalsifierRegistryRow(
        intervention_count_d3=len(d3_items),
        registry_falsifiers=tuple(sorted(registry_fals)),
        causal_doc_falsifiers=tuple(sorted(causal_fals)),
        linked=tuple(sorted(linked & REQUIRED_BOUNDARY_FALSIFIERS)),
        missing=tuple(missing),
        ok=ok,
    )


def run_governor_gate_smoke(repo: Path) -> GovernorGateRow:
    main_src = repo / "src"
    if str(main_src) not in sys.path:
        sys.path.insert(0, str(main_src))

    from eia.governor import ContactGovernor, GovernorConfig
    from eia.schemas.contact import ContactOutcome
    from eia.schemas.initiative import Initiative, InitiativeCandidate, InitiativeKind

    intervention_cube = _load_woe_submodule(repo, "intervention_cube")
    cf7_present = any(i.id == "do_z_governor_isolation" for i in intervention_cube.list_all())

    gov = ContactGovernor(GovernorConfig(min_contact_score=0.99, min_evsi=0.99))
    init = Initiative(
        id="boundary-witness-low",
        timestamp=datetime.now(timezone.utc),
        candidate=InitiativeCandidate(
            id="c-boundary-low",
            kind=InitiativeKind.ASK_QUESTION,
            expected_info_gain=0.05,
            interrupt_cost=0.5,
        ),
        abstained=False,
        parent_motivation_id="m-boundary",
        evsi=0.05,
    )
    decision = gov.evaluate(init)
    deny_low = decision.outcome == ContactOutcome.DENY
    ok = deny_low and cf7_present
    return GovernorGateRow(
        deny_low_value=deny_low,
        min_contact_score=gov.config.min_contact_score,
        cf7_intervention_present=cf7_present,
        ok=ok,
    )


def run_att_n_boundary_smoke(repo: Path, *, n_seeds: int = 2) -> AttNBoundaryRow:
    non_embeddability = _load_woe_submodule(repo, "non_embeddability")
    batch = non_embeddability.run_att_n_batch(n_seeds=n_seeds)
    causal = batch["by_arm"].get("causal_loss_under_b", {})
    rate = causal.get("att_n_evidence_rate")
    if rate is not None:
        rate = float(rate)
    ok = (
        batch.get("claim_allowed") is False
        and batch.get("n_h_claim") is False
        and batch.get("agi_star_claim") is False
        and n_seeds >= 1
    )
    return AttNBoundaryRow(
        n_seeds=n_seeds,
        causal_att_n_rate=rate,
        claim_allowed=bool(batch.get("claim_allowed")),
        n_h_claim=bool(batch.get("n_h_claim")),
        ok=ok,
    )


def run_namm_soft_witness(repo: Path) -> NammSoftWitnessRow:
    namm_dir = repo / "traces" / "namm_intents"
    if not namm_dir.is_dir():
        return NammSoftWitnessRow(
            intent_files=0,
            valid_json=0,
            domains=(),
            tier="B",
            ok=False,
        )

    files = list(namm_dir.glob("*.json"))
    valid = 0
    domains: set[str] = set()
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if payload.get("kind") == "namm_hook" and "hook_id" in payload:
            valid += 1
            domain = payload.get("domain")
            if isinstance(domain, str):
                domains.add(domain)

    ok = valid > 0
    return NammSoftWitnessRow(
        intent_files=len(files),
        valid_json=valid,
        domains=tuple(sorted(domains)),
        tier="B",
        ok=ok,
    )


def run_boundary_witness(
    repo: Path,
    *,
    att_n_seeds: int = 2,
) -> BoundaryWitnessResult:
    """Run D3×L3 boundary witness checks (Tier B soft N_H; claim_allowed=false)."""
    falsifier = run_falsifier_registry_smoke(repo)
    governor = run_governor_gate_smoke(repo)
    att_n = run_att_n_boundary_smoke(repo, n_seeds=att_n_seeds)
    namm = run_namm_soft_witness(repo)

    hard_ok = falsifier.ok and governor.ok and att_n.ok
    witness_tier: WitnessTier = "B_soft_NH" if namm.ok else "B_partial"
    passed = hard_ok

    if namm.ok:
        note = (
            "D3×L3 boundary witness: falsifier registry + governor gate + ATT-N explore; "
            "NAMM intent corpus Tier B soft witness (not strong N_H)."
        )
    else:
        note = (
            "D3×L3 boundary witness: falsifier registry + governor gate + ATT-N explore; "
            "NAMM soft witness absent — Tier B partial only."
        )

    return BoundaryWitnessResult(
        falsifier_registry=falsifier,
        governor_gate=governor,
        att_n=att_n,
        namm_soft=namm,
        witness_tier=witness_tier,
        claim_ceiling="C2",
        claim_allowed=False,
        n_h_claim=False,
        agi_star_claim=False,
        passed=passed,
        note=note,
    )
