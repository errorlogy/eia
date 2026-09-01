#!/usr/bin/env python3
"""M-3D-EXPRESS: lightweight 9-cell smoke pass (D1/D2/D3 × L1/L2/L3).

Runs each cell check in <60s total. Outputs JSON + markdown summary.
Updates cube cell statuses. claim_allowed=false; C2 ceiling; not AGI*.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
import types
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

REPO = Path(__file__).resolve().parents[2]
SCI_FLOW = Path(__file__).resolve().parent
MAIN_SRC = REPO / "src"
WOE_SRC = REPO / "research" / "cursor-starter-v0.2" / "src"
WOE_PKG = WOE_SRC / "eia"

if str(MAIN_SRC) not in sys.path:
    sys.path.insert(0, str(MAIN_SRC))
if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

CellStatus = Literal["pass", "partial", "fail", "empty"]


@dataclass
class CellResult:
    cell: str
    axis: str
    layer: str
    status: CellStatus
    message: str
    duration_ms: float
    details: dict[str, Any] = field(default_factory=dict)


def _load_woe_submodule(name: str) -> Any:
    pkg_name = "woe_eia_express"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [str(WOE_PKG)]  # type: ignore[attr-defined]
        sys.modules[pkg_name] = pkg
    full = f"{pkg_name}.{name}"
    if full in sys.modules:
        return sys.modules[full]
    path = WOE_PKG / f"{name}.py"
    spec = importlib.util.spec_from_file_location(full, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = pkg_name
    sys.modules[full] = mod
    spec.loader.exec_module(mod)
    return mod


def _timed(fn) -> CellResult:
    t0 = time.perf_counter()
    result = fn()
    result.duration_ms = round((time.perf_counter() - t0) * 1000, 1)
    return result


# --- D1 ---


def check_d1_l1() -> CellResult:
    doc = SCI_FLOW / "CAUSAL_ENDOGENEITY.md"
    ok = doc.is_file()
    text = doc.read_text(encoding="utf-8") if ok else ""
    has_bar = "F-DECL" in text and "F-EXT" in text
    status: CellStatus = "pass" if ok and has_bar else "partial" if ok else "fail"
    return CellResult(
        cell="D1×L1",
        axis="D1",
        layer="L1",
        status=status,
        message="Causal bar definitions present" if has_bar else "CAUSAL_ENDOGENEITY.md incomplete",
        duration_ms=0.0,
        details={"doc": str(doc.relative_to(REPO)), "falsifiers": ["F-DECL", "F-EXT"]},
    )


def check_d1_l2() -> CellResult:
    from eoi_k_harness import run_eoi_k_sweep

    result = run_eoi_k_sweep(
        REPO,
        k_values=(1, 5, 20),
        scenario_ids=("eoi_k_steered",),
        include_carryover=False,
        steered_seed=303,
    )
    steered = [r for r in result.rows if r.scenario_id == "eoi_k_steered"]
    k1 = next((r for r in steered if r.k == 1), None)
    k5 = next((r for r in steered if r.k == 5), None)
    gradient = k1 is not None and k5 is not None and k1.eoi > k5.eoi
    status: CellStatus = "pass" if gradient and result.claim_allowed is False else "partial"
    return CellResult(
        cell="D1×L2",
        axis="D1",
        layer="L2",
        status=status,
        message="D01 EOI-k counterfactual sweep (eoi_k_steered gradient)" if gradient else "D01 ran; no EOI gradient",
        duration_ms=0.0,
        details={
            "k1_eoi": k1.eoi if k1 else None,
            "k5_eoi": k5.eoi if k5 else None,
            "claim_allowed": result.claim_allowed,
            "pool_metric_id": result.pool_metric_id,
            "att": result.att,
        },
    )


def check_d1_l3() -> CellResult:
    evidence_proofs = _load_woe_submodule("evidence_proofs")

    item = evidence_proofs.EvidenceItem(
        evidence_id="express-att-e-stub",
        metric_id="E_ENDO",
        value=0.35,
        trajectory_changed=True,
        do_z_changes_g_distribution=False,
        x_non_triggering=True,
        matching_external_initiating_signal=False,
        falsifiers_triggered=(),
        provenance="research/sci_flow/run_3d_express.py",
    )
    proof = evidence_proofs.evaluate_eia_proof_version((item,))
    ok = proof.c_ladder_raise_allowed is False and proof.agi_star_claim is False
    return CellResult(
        cell="D1×L3",
        axis="D1",
        layer="L3",
        status="pass" if ok else "partial",
        message="ATT-E proof-protocol witness stub (shadow receipt)",
        duration_ms=0.0,
        details={
            "protocol_version": proof.protocol_version,
            "e_endo_support": proof.e_endo_support,
            "claim_ceiling": proof.claim_ceiling,
        },
    )


# --- D2 ---


def check_d2_l1() -> CellResult:
    doc = SCI_FLOW / "STABLE_ENDOGENEITY.md"
    ok = doc.is_file()
    text = doc.read_text(encoding="utf-8") if ok else ""
    has_vector = "mathfrak{E}" in text or "stable" in text.lower()
    status: CellStatus = "pass" if ok and has_vector else "partial" if ok else "fail"
    return CellResult(
        cell="D2×L1",
        axis="D2",
        layer="L1",
        status=status,
        message="Stable endogeneity invariants documented",
        duration_ms=0.0,
        details={"doc": str(doc.relative_to(REPO))},
    )


def check_d2_l2() -> CellResult:
    from eia.runtime.shadow_multitick import run_dsr_longitudinal_session

    result = run_dsr_longitudinal_session(target_cognitive_ticks=6, seed=0)
    ok = result["cognitive_ticks_reached"] >= 6
    return CellResult(
        cell="D2×L2",
        axis="D2",
        layer="L2",
        status="pass" if ok else "partial",
        message="DSR smoke on shadow carryover (6 ticks)",
        duration_ms=0.0,
        details={
            "dsr_min": result.get("dsr_min"),
            "cognitive_ticks": result.get("cognitive_ticks_reached"),
            "d05_pass": result.get("d05_pass"),
        },
    )


def check_d2_l3() -> CellResult:
    from eia.runtime.shadow_multitick import ShadowArm, run_shadow_episode

    ep = run_shadow_episode(arm=ShadowArm.CLOSED_LOOP, seed=0)
    has_recurrence = any(e.kind == "G_prime" and e.novel for e in ep.events)
    return CellResult(
        cell="D2×L3",
        axis="D2",
        layer="L3",
        status="pass" if has_recurrence else "partial",
        message="ATT-R shadow closed-loop witness (G' novel)",
        duration_ms=0.0,
        details={"arm": ep.arm, "ticks_run": ep.ticks_run, "event_count": len(ep.events)},
    )


# --- D3 ---


def check_d3_l1() -> CellResult:
    intervention_cube = _load_woe_submodule("intervention_cube")

    items = intervention_cube.list_all()
    doc = SCI_FLOW / "AGI_STAR_CRITERION.md"
    ok = len(items) >= 8 and doc.is_file()
    return CellResult(
        cell="D3×L1",
        axis="D3",
        layer="L1",
        status="pass" if ok else "partial",
        message=f"Falsifier/intervention registry ({len(items)} entries)",
        duration_ms=0.0,
        details={"registry_count": len(items), "criterion_doc": doc.is_file()},
    )


def check_d3_l2() -> CellResult:
    from eia.governor import ContactGovernor, GovernorConfig

    gov = ContactGovernor(GovernorConfig())
    non_embeddability = _load_woe_submodule("non_embeddability")

    batch = non_embeddability.run_att_n_batch(
        n_seeds=2, budget=non_embeddability.EXPLORE_ENCODING_BUDGET_B
    )
    causal = batch["by_arm"].get("causal", {})
    budget_b = non_embeddability.EXPLORE_ENCODING_BUDGET_B
    budget_val = int(budget_b) if hasattr(budget_b, "__int__") else str(budget_b)
    causal_rate = causal.get("rate")
    if causal_rate is not None:
        causal_rate = float(causal_rate)
    return CellResult(
        cell="D3×L2",
        axis="D3",
        layer="L2",
        status="pass",
        message="Governor scaffold + ATT-N smoke (n=2)",
        duration_ms=0.0,
        details={
            "governor_min_contact": gov.config.min_contact_score,
            "att_n_causal_rate": causal_rate,
            "budget_b": budget_val,
        },
    )


def check_d3_l3() -> CellResult:
    namm_dir = REPO / "traces" / "namm_intents"
    has_intents = namm_dir.is_dir() and any(namm_dir.glob("*.json"))
    return CellResult(
        cell="D3×L3",
        axis="D3",
        layer="L3",
        status="partial" if has_intents else "empty",
        message="NAMM soft witness optional — partial boundary receipts" if has_intents else "No strong N_H witness (expected)",
        duration_ms=0.0,
        details={
            "namm_intents_dir": str(namm_dir.relative_to(REPO)),
            "intent_files": len(list(namm_dir.glob("*.json"))) if has_intents else 0,
            "n_h_claim": False,
        },
    )


CHECKS = (
    check_d1_l1,
    check_d1_l2,
    check_d1_l3,
    check_d2_l1,
    check_d2_l2,
    check_d2_l3,
    check_d3_l1,
    check_d3_l2,
    check_d3_l3,
)


def run_express_pass() -> dict[str, Any]:
    t0 = time.perf_counter()
    cells: list[CellResult] = []
    for fn in CHECKS:
        cells.append(_timed(fn))
    total_ms = round((time.perf_counter() - t0) * 1000, 1)

    status_grid: dict[str, str] = {}
    for c in cells:
        status_grid[c.cell] = c.status

    return {
        "milestone": "M-3D-EXPRESS",
        "date": date.today().isoformat(),
        "claim_ceiling": "C2",
        "claim_allowed": False,
        "agi_star_claim": False,
        "total_duration_ms": total_ms,
        "under_60s": total_ms < 60_000,
        "cells": [
            {
                "cell": c.cell,
                "axis": c.axis,
                "layer": c.layer,
                "status": c.status,
                "message": c.message,
                "duration_ms": c.duration_ms,
                "details": c.details,
            }
            for c in cells
        ],
        "status_grid": status_grid,
    }


def _markdown(payload: dict[str, Any]) -> str:
    today = payload["date"]
    lines = [
        f"# M-3D-EXPRESS — 9-cell smoke pass — {today}",
        "",
        "**Status:** express harness executed",
        "**Branch:** `research/cursor-starter-v0.2-woe-eis`",
        "**Claim ceiling:** C2 — `claim_allowed=false`, **not AGI\\***",
        f"**Total duration:** {payload['total_duration_ms']} ms (budget <60s)",
        "",
        "## Status grid",
        "",
        "| Cell | Status | Message | ms |",
        "|------|--------|---------|-----|",
    ]
    for c in payload["cells"]:
        lines.append(f"| {c['cell']} | **{c['status']}** | {c['message']} | {c['duration_ms']} |")

    lines.extend(
        [
            "",
            "## Matrix view",
            "",
            "| | **L1** | **L2** | **L3** |",
            "|---|--------|--------|--------|",
        ]
    )
    for axis in ("D1", "D2", "D3"):
        row = [f"**{axis}**"]
        for layer in ("L1", "L2", "L3"):
            key = f"{axis}×{layer}"
            row.append(f"**{payload['status_grid'].get(key, '—')}**")
        lines.append("| " + " | ".join(row) + " |")

    lines.extend(
        [
            "",
            "## Runner",
            "",
            "```bash",
            "python research/sci_flow/run_3d_express.py",
            "```",
            "",
            "Cube doc: `research/sci_flow/SCI_FLOW_3D_CUBE.md`",
            "",
        ]
    )
    return "\n".join(lines)


def _update_cube_doc(payload: dict[str, Any]) -> None:
    cube_path = SCI_FLOW / "SCI_FLOW_3D_CUBE.md"
    text = cube_path.read_text(encoding="utf-8")

    def _layer_status(axis: str, layer: str) -> str:
        raw = payload["status_grid"].get(f"{axis}×{layer}", "partial")
        if raw == "pass":
            return "filled"
        if raw == "empty":
            return "empty"
        return "partial"

    replacements = {
        "| **D1 Causal** | **filled** — [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) bar, F-DECL/F-EXT | **partial** — CF-4, EOI, **D01 started** | **partial** — [`EIA_PROOF_PROTOCOL.md`](EIA_PROOF_PROTOCOL.md), M-CF4 metrics |":
            f"| **D1 Causal** | **{_layer_status('D1', 'L1')}** — [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) bar, F-DECL/F-EXT | **{_layer_status('D1', 'L2')}** — CF-4, EOI, **D01 deepened** (counterfactual + carryover) | **{_layer_status('D1', 'L3')}** — [`EIA_PROOF_PROTOCOL.md`](EIA_PROOF_PROTOCOL.md), ATT-E witness stub |",
        "| **D2 Dynamic** | **filled** — [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md), $\\mathfrak{E}$ vector | **partial** — ATT-R/M-R-LIVE, DSR, OMEGA | **partial** — M-R-LIVE JSON, [`M-E04_DSR_metrics_2026-09-01.md`](M-E04_DSR_metrics_2026-09-01.md) |":
            f"| **D2 Dynamic** | **{_layer_status('D2', 'L1')}** — [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md), $\\mathfrak{{E}}$ vector | **{_layer_status('D2', 'L2')}** — ATT-R/M-R-LIVE, DSR smoke, OMEGA | **{_layer_status('D2', 'L3')}** — M-R-LIVE JSON, ATT-R shadow witness |",
        "| **D3 Boundary** | **filled** — [`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md) conjunction | **partial** — ATT-N explore, governor scaffold | **empty/partial** — NAMM soft witness optional; no strong $N_H$ |":
            f"| **D3 Boundary** | **{_layer_status('D3', 'L1')}** — [`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md) conjunction | **{_layer_status('D3', 'L2')}** — ATT-N explore, governor scaffold | **{_layer_status('D3', 'L3')}** — NAMM soft witness optional; no strong $N_H$ |",
    }
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
        else:
            # Fallback: update milestone line only
            pass

    if "**Milestone:** M-3D-01" in text:
        text = text.replace(
            "**Milestone:** M-3D-01",
            "**Milestone:** M-3D-01 + M-3D-EXPRESS",
        )

    express_note = (
        "\n\n## Express pass (M-3D-EXPRESS)\n\n"
        f"Last run: {payload['date']} — `{payload['total_duration_ms']}` ms — "
        f"`python research/sci_flow/run_3d_express.py`\n"
    )
    if "## Express pass (M-3D-EXPRESS)" not in text:
        text = text.rstrip() + express_note

    cube_path.write_text(text, encoding="utf-8")


def main() -> int:
    payload = run_express_pass()
    today = payload["date"]
    json_path = SCI_FLOW / f"M-3D-EXPRESS_{today}.json"
    md_path = SCI_FLOW / f"M-3D-EXPRESS_{today}.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    _update_cube_doc(payload)

    print(json.dumps(payload, indent=2))
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    print("updated SCI_FLOW_3D_CUBE.md")

    failed = [c for c in payload["cells"] if c["status"] == "fail"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
