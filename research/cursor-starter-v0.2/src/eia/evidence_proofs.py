"""Versioned evidence/proof protocol for EIA sci-flow research.

This module turns reported sci-flow observations into a conservative proof
version record. It is intentionally a classifier/ledger, not a production gate:
no AGI* claim, no automatic C-ladder raise, and C2 remains the active ceiling.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

try:  # normal package import
    from .agi_transition import e_endo_label_admissible
    from .endogeneity_metrics import get_metric
except ImportError:  # direct importlib loading in tests
    from eia.agi_transition import e_endo_label_admissible  # type: ignore
    from eia.endogeneity_metrics import get_metric  # type: ignore

PROTOCOL_VERSION = "sci-flow-eia-proof-v0.1"
ACTIVE_CLAIM_CEILING = "C2"

SupportLevel = Literal["none", "partial"]

# Falsifiers canonicalized from CAUSAL_ENDOGENEITY.md / metrics pool.
SCOPED_E_ENDO_METRICS = frozenset({"E_ENDO", "CF4_E_PARTIAL", "E_C", "C_INT"})


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    """One pre-registered observation submitted to the proof protocol."""

    evidence_id: str
    metric_id: str
    value: float | None
    trajectory_changed: bool
    do_z_changes_g_distribution: bool
    x_non_triggering: bool
    matching_external_initiating_signal: bool
    falsifiers_triggered: tuple[str, ...] = ()
    provenance: str = ""
    agency_label: str = "instrumented_causal_evidence"


@dataclass(frozen=True, slots=True)
class EIAProofVersion:
    """Conservative sci-flow proof-version output."""

    protocol_version: str
    claim_ceiling: str
    e_endo_support: SupportLevel
    accepted_evidence_ids: tuple[str, ...]
    rejected_evidence_ids: tuple[str, ...]
    falsifier_ids: tuple[str, ...]
    c_ladder_raise_allowed: bool
    agi_star_claim: bool
    rationale: str


def _lookup_metric_claim(metric_id: str, pool_path: Path | None) -> str | bool:
    try:
        return get_metric(metric_id, path=pool_path).claim_allowed
    except (FileNotFoundError, KeyError):
        return False


def _item_falsifiers(item: EvidenceItem, *, pool_path: Path | None) -> tuple[str, ...]:
    """Derive falsifiers from explicit flags and causal-bar failures."""
    falsifiers: set[str] = {str(f) for f in item.falsifiers_triggered}

    metric_claim = _lookup_metric_claim(item.metric_id, pool_path)
    if metric_claim in (False, "false") and item.metric_id not in SCOPED_E_ENDO_METRICS:
        falsifiers.add("NON_TIER_A_OR_NON_CLAIMABLE")

    if item.metric_id == "NM_DECL":
        falsifiers.add("F-DECL")
    if item.metric_id in {"OMEGA_T", "O_T", "KURAMOTO_R", "NM_SYNC_ONLY"}:
        falsifiers.add("F-SYNC")
    if not item.trajectory_changed:
        falsifiers.add("F-NARR")
    if item.matching_external_initiating_signal:
        falsifiers.add("F-EXT")
    if not item.do_z_changes_g_distribution:
        falsifiers.add("F-NODO")
    if not item.x_non_triggering:
        falsifiers.add("F-EXT")

    return tuple(sorted(falsifiers))


def _item_admissible(item: EvidenceItem, *, pool_path: Path | None) -> bool:
    if item.metric_id not in SCOPED_E_ENDO_METRICS:
        return False
    if _lookup_metric_claim(item.metric_id, pool_path) in (False, "false"):
        return False
    if _item_falsifiers(item, pool_path=pool_path):
        return False
    return e_endo_label_admissible(
        agency_label=item.agency_label,
        trajectory_changed=item.trajectory_changed,
        matching_external_initiating_signal=item.matching_external_initiating_signal,
        do_z_changes_g_distribution=item.do_z_changes_g_distribution,
        x_non_triggering=item.x_non_triggering,
    )


def evaluate_eia_proof_version(
    evidence: tuple[EvidenceItem, ...] | list[EvidenceItem],
    *,
    pool_path: Path | None = None,
) -> EIAProofVersion:
    """Evaluate reported sci-flow evidence under proof protocol v0.1.

    The only positive output currently possible is ``e_endo_support='partial'``.
    ``agi_star_claim`` and ``c_ladder_raise_allowed`` are hard false by design.
    """
    accepted: list[str] = []
    rejected: list[str] = []
    falsifiers: set[str] = set()

    for item in evidence:
        item_falsifiers = _item_falsifiers(item, pool_path=pool_path)
        falsifiers.update(item_falsifiers)
        if _item_admissible(item, pool_path=pool_path):
            accepted.append(item.evidence_id)
        else:
            rejected.append(item.evidence_id)

    support: SupportLevel = "partial" if accepted else "none"
    rationale = (
        "Scoped ATT-E / CF-4-class causal evidence accepted; claim remains "
        "partial C2 only; N_H/P/R/D conjunction unmeasured or non-claimable."
        if accepted
        else "No admissible Tier-A causal evidence after falsifier and causal-bar checks."
    )

    return EIAProofVersion(
        protocol_version=PROTOCOL_VERSION,
        claim_ceiling=ACTIVE_CLAIM_CEILING,
        e_endo_support=support,
        accepted_evidence_ids=tuple(accepted),
        rejected_evidence_ids=tuple(rejected),
        falsifier_ids=tuple(sorted(falsifiers)),
        c_ladder_raise_allowed=False,
        agi_star_claim=False,
        rationale=rationale,
    )


def evidence_item_to_dict(item: EvidenceItem) -> dict[str, Any]:
    """Serialize one evidence item for dated ledger artifacts."""
    return {
        "evidence_id": item.evidence_id,
        "metric_id": item.metric_id,
        "value": item.value,
        "trajectory_changed": item.trajectory_changed,
        "do_z_changes_g_distribution": item.do_z_changes_g_distribution,
        "x_non_triggering": item.x_non_triggering,
        "matching_external_initiating_signal": item.matching_external_initiating_signal,
        "falsifiers_triggered": list(item.falsifiers_triggered),
        "provenance": item.provenance,
        "agency_label": item.agency_label,
    }


def proof_version_to_dict(proof: EIAProofVersion) -> dict[str, Any]:
    """Serialize proof-version output for ledger JSON."""
    return {
        "protocol_version": proof.protocol_version,
        "claim_ceiling": proof.claim_ceiling,
        "e_endo_support": proof.e_endo_support,
        "accepted_evidence_ids": list(proof.accepted_evidence_ids),
        "rejected_evidence_ids": list(proof.rejected_evidence_ids),
        "falsifier_ids": list(proof.falsifier_ids),
        "c_ladder_raise_allowed": proof.c_ladder_raise_allowed,
        "agi_star_claim": proof.agi_star_claim,
        "rationale": proof.rationale,
    }


def evidence_item_from_cf4_summary(
    summary: dict[str, Any],
    *,
    provenance: str,
    evidence_id: str = "M-CF4-do_z-epistemic_gap",
) -> EvidenceItem:
    """Map CF-4 summary block to a scoped ATT-E evidence item."""
    default = summary["conditions"]["default"]
    epistemic_gap = summary["conditions"]["zero_epistemic_gap"]
    intent_delta = float(default["intent_rate"]) - float(epistemic_gap["intent_rate"])
    return EvidenceItem(
        evidence_id=evidence_id,
        metric_id="CF4_E_PARTIAL",
        value=round(intent_delta, 4),
        trajectory_changed=bool(summary.get("c2_claim")),
        do_z_changes_g_distribution=True,
        x_non_triggering=True,
        matching_external_initiating_signal=False,
        falsifiers_triggered=(),
        provenance=provenance,
        agency_label="instrumented_causal_evidence",
    )


def evidence_item_from_d01_row(
    row: dict[str, Any],
    *,
    provenance: str,
) -> EvidenceItem:
    """Map one D01 EOI-k row to an E_ENDO explore witness (do_x intervention)."""
    original = row.get("original_target")
    twin = row.get("twin_target")
    trajectory_changed = (
        original is not None and twin is not None and original != twin
    )
    scenario_id = str(row["scenario_id"])
    k = int(row["k"])
    return EvidenceItem(
        evidence_id=f"M-D01-{scenario_id}-k{k}",
        metric_id="E_ENDO",
        value=float(row["eoi"]),
        trajectory_changed=trajectory_changed,
        do_z_changes_g_distribution=False,
        x_non_triggering=True,
        matching_external_initiating_signal=False,
        falsifiers_triggered=(),
        provenance=provenance,
        agency_label="instrumented_causal_evidence",
    )


def build_d1_l3_evidence_from_artifacts(
    cf4_payload: dict[str, Any],
    d01_payload: dict[str, Any],
    *,
    cf4_provenance: str,
    d01_provenance: str,
) -> tuple[EvidenceItem, ...]:
    """Build empirical D1×L3 evidence batch from CF-4 + D01 L2 artifacts."""
    items: list[EvidenceItem] = [
        evidence_item_from_cf4_summary(
            cf4_payload["summary"],
            provenance=cf4_provenance,
        )
    ]
    for row in d01_payload.get("rows", []):
        if str(row.get("scenario_id")) != "eoi_k_steered":
            continue
        items.append(
            evidence_item_from_d01_row(row, provenance=d01_provenance),
        )
    return tuple(items)


def evaluate_d1_l3_proof_ledger(
    evidence: tuple[EvidenceItem, ...] | list[EvidenceItem],
    *,
    pool_path: Path | None = None,
    tick_id: str = "M-D1-L3-LEDGER",
    cell: str = "D1×L3",
    sources: dict[str, str] | None = None,
    generated: str | None = None,
) -> dict[str, Any]:
    """Evaluate empirical evidence and return a dated D1×L3 ledger record."""
    proof = evaluate_eia_proof_version(evidence, pool_path=pool_path)
    return {
        "tick_id": tick_id,
        "cell": cell,
        "generated": generated,
        "claim_ceiling": proof.claim_ceiling,
        "claim_allowed": False,
        "e_endo_support": proof.e_endo_support,
        "c_ladder_raise_allowed": proof.c_ladder_raise_allowed,
        "agi_star_claim": proof.agi_star_claim,
        "sources": sources or {},
        "evidence_items": [evidence_item_to_dict(item) for item in evidence],
        "proof": proof_version_to_dict(proof),
    }


def load_d1_l3_ledger_artifacts(
    sci_flow_dir: Path,
    *,
    cf4_name: str = "cf4_results.json",
    d01_name: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    """Load CF-4 and D01 JSON artifacts from ``research/sci_flow``."""
    cf4_path = sci_flow_dir / cf4_name
    if not cf4_path.is_file():
        raise FileNotFoundError(f"CF-4 artifact missing: {cf4_path}")

    if d01_name is None:
        candidates = sorted(sci_flow_dir.glob("M-D01_EOI_k_metrics_*.json"))
        if not candidates:
            raise FileNotFoundError("D01 EOI-k artifact missing under research/sci_flow")
        d01_path = candidates[-1]
    else:
        d01_path = sci_flow_dir / d01_name
        if not d01_path.is_file():
            raise FileNotFoundError(f"D01 artifact missing: {d01_path}")

    cf4_payload = json.loads(cf4_path.read_text(encoding="utf-8"))
    d01_payload = json.loads(d01_path.read_text(encoding="utf-8"))
    repo_root = sci_flow_dir.parents[1]

    def _rel(path: Path) -> str:
        try:
            return path.relative_to(repo_root).as_posix()
        except ValueError:
            return path.as_posix()

    sources = {
        "cf4": _rel(cf4_path),
        "d01": _rel(d01_path),
        "cf4_md": "research/sci_flow/M-CF4_metrics_2026-08-20.md",
        "protocol": "research/sci_flow/EIA_PROOF_PROTOCOL.md",
    }
    return cf4_payload, d01_payload, sources


def render_proof_report(proof: EIAProofVersion) -> str:
    """Render a stable markdown summary for sci-flow logs."""
    accepted = ", ".join(proof.accepted_evidence_ids) or "—"
    rejected = ", ".join(proof.rejected_evidence_ids) or "—"
    falsifiers = ", ".join(proof.falsifier_ids) or "—"
    return "\n".join(
        (
            f"# EIA Proof Protocol Report — {proof.protocol_version}",
            "",
            f"Claim ceiling: {proof.claim_ceiling}",
            f"E_endo support: {proof.e_endo_support}",
            "C-ladder raise allowed: false",
            "AGI*: false",
            f"Accepted evidence: {accepted}",
            f"Rejected evidence: {rejected}",
            f"Falsifiers: {falsifiers}",
            "",
            proof.rationale,
        )
    )
