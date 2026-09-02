"""M-O proof adjunct bridge — Neuraxon/native arms → D2×L3 witness ledger.

Maps paired do(O) arm payloads to ``MOAdjunctEvidenceItem`` records and evaluates
them under ``sci-flow-mo-adjunct-v0.1``. Tier C only; ``claim_allowed=false``;
no bleed to D1 ``e_endo_support``.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCI_FLOW = Path(__file__).resolve().parent
_SRC = REPO / "research" / "cursor-starter-v0.2" / "src"
ARMS_ARTIFACT = SCI_FLOW / "M-MO_do_o_arms_2026-09-02.json"
ADJUNCT_ARTIFACT_JSON = SCI_FLOW / "M-MO_proof_adjunct_2026-09-02.json"
ADJUNCT_ARTIFACT_MD = SCI_FLOW / "M-MO_proof_adjunct_2026-09-02.md"


def _load_evidence_proofs() -> Any:
    import importlib.util

    if str(_SRC) not in sys.path:
        sys.path.insert(0, str(_SRC))
    eia_dir = _SRC / "eia"
    for submodule in ("agi_transition", "endogeneity_metrics"):
        full_name = f"eia.{submodule}"
        if full_name not in sys.modules:
            sub_path = eia_dir / f"{submodule}.py"
            sub_spec = importlib.util.spec_from_file_location(full_name, sub_path)
            if sub_spec is None or sub_spec.loader is None:
                raise ImportError(f"cannot load {sub_path}")
            sub_mod = importlib.util.module_from_spec(sub_spec)
            sys.modules[full_name] = sub_mod
            sub_spec.loader.exec_module(sub_mod)

    mod_path = eia_dir / "evidence_proofs.py"
    spec = importlib.util.spec_from_file_location("eia_evidence_proofs_mo_bridge", mod_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load evidence_proofs from {mod_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def load_arms_payload(
    arms_path: Path = ARMS_ARTIFACT,
    *,
    regenerate: bool = False,
    steps: int = 50,
    seed: int = 42,
) -> dict[str, Any]:
    """Load paired do(O) arms artifact, optionally regenerating it first."""
    if regenerate or not arms_path.is_file():
        import importlib.util

        arms_script = SCI_FLOW / "run_mo_do_o_arms.py"
        spec = importlib.util.spec_from_file_location("run_mo_do_o_arms_bridge", arms_script)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load {arms_script}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        payload = mod.build_payload(steps=steps, seed=seed)
        arms_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload
    return json.loads(arms_path.read_text(encoding="utf-8"))


def build_adjunct_ledger(
    arms_payload: dict[str, Any],
    *,
    generated: str | None = None,
) -> dict[str, Any]:
    """Build D2×L3 M-O adjunct ledger from paired arms payload."""
    ep = _load_evidence_proofs()
    provenance = _rel(ARMS_ARTIFACT)
    evidence = ep.build_mo_adjunct_evidence_from_arms_payload(
        arms_payload,
        provenance=provenance,
    )
    sources = {
        "arms": provenance,
        "protocol": "research/sci_flow/EIA_PROOF_PROTOCOL.md",
        "admissibility": "research/sci_flow/M-O_PROOF_ADMISSIBILITY.md",
        "implementation": "research/cursor-starter-v0.2/src/eia/evidence_proofs.py",
    }
    return ep.evaluate_mo_adjunct_ledger(
        evidence,
        tick_id="M-MO-PROOF-ADJUNCT",
        sources=sources,
        generated=generated or date.today().isoformat(),
        arms_payload=arms_payload,
    )


def render_adjunct_markdown(ledger: dict[str, Any]) -> str:
    """Render adjunct ledger markdown artifact."""
    ep = _load_evidence_proofs()
    proof_dict = ledger["proof"]
    proof = ep.MOAdjunctProofVersion(
        protocol_version=proof_dict["protocol_version"],
        claim_ceiling=proof_dict["claim_ceiling"],
        witness_support=proof_dict["witness_support"],
        e_endo_support=proof_dict["e_endo_support"],
        accepted_evidence_ids=tuple(proof_dict["accepted_evidence_ids"]),
        rejected_evidence_ids=tuple(proof_dict["rejected_evidence_ids"]),
        falsifier_ids=tuple(proof_dict["falsifier_ids"]),
        annotation_falsifier_ids=tuple(proof_dict["annotation_falsifier_ids"]),
        c_ladder_raise_allowed=proof_dict["c_ladder_raise_allowed"],
        agi_star_claim=proof_dict["agi_star_claim"],
        claim_allowed=proof_dict["claim_allowed"],
        rationale=proof_dict["rationale"],
    )
    lines = [
        render_adjunct_report_header(ledger),
        "",
        ep.render_mo_adjunct_report(proof),
        "",
        "## Evidence items",
        "",
    ]
    for item in ledger.get("evidence_items", []):
        lines.append(
            f"- `{item['evidence_id']}`: {item['metric_id']} "
            f"Δ={item['metric_delta']} ({item['intervention_id']})"
        )
    lines.extend(
        [
            "",
            "## Invariants",
            "",
            "- `e_endo_support=none` (no D1 bleed)",
            "- `claim_allowed=false`",
            "- `c_ladder_raise_allowed=false`",
            "- `agi_star_claim=false`",
            "- Kuramoto R ≠ E_endo (F-KURAMOTO-AS-E annotation when R high)",
        ]
    )
    return "\n".join(lines)


def render_adjunct_report_header(ledger: dict[str, Any]) -> str:
    """Short artifact header for markdown."""
    arms = ledger.get("arms_summary") or {}
    return "\n".join(
        (
            f"# M-MO Proof Adjunct — {ledger.get('generated', '')}",
            "",
            f"**Cell:** {ledger.get('cell', 'D2×L3')} · **Tier:** {ledger.get('tier', 'C')} · "
            f"**Evidence class:** `{ledger.get('evidence_class', 'mo_tier_c_witness')}`",
            f"**Arms:** `{arms.get('artifact_id', '')}` seed={arms.get('seed')} steps={arms.get('steps')}",
        )
    )
