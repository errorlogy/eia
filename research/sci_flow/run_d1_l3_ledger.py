"""D1×L3 empirical proof ledger — CF-4 + D01 → EvidenceItem batch.

Writes dated JSON artifact for cell_registry D1.L3. Tier 0: no LLM, no AGI*.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "cursor-starter-v0.2" / "src"


def _load_evidence_proofs():
    """Load research-branch evidence_proofs even when main ``eia`` is on sys.path."""
    import importlib.util

    if str(_SRC) not in sys.path:
        sys.path.insert(0, str(_SRC))
    mod_path = _SRC / "eia" / "evidence_proofs.py"
    spec = importlib.util.spec_from_file_location("eia_evidence_proofs_ledger", mod_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load evidence_proofs from {mod_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ep = _load_evidence_proofs()
build_d1_l3_evidence_from_artifacts = _ep.build_d1_l3_evidence_from_artifacts
evaluate_d1_l3_proof_ledger = _ep.evaluate_d1_l3_proof_ledger
evaluate_eia_proof_version = _ep.evaluate_eia_proof_version
load_d1_l3_ledger_artifacts = _ep.load_d1_l3_ledger_artifacts
render_proof_report = _ep.render_proof_report

SCI_FLOW = Path(__file__).resolve().parent


def build_ledger(
    sci_flow_dir: Path = SCI_FLOW,
    *,
    generated: str | None = None,
    d01_name: str | None = "M-D01_EOI_k_metrics_2026-09-01.json",
) -> dict:
    """Build D1×L3 ledger dict from on-disk CF-4 and D01 artifacts."""
    cf4_payload, d01_payload, sources = load_d1_l3_ledger_artifacts(
        sci_flow_dir,
        d01_name=d01_name,
    )
    evidence = build_d1_l3_evidence_from_artifacts(
        cf4_payload,
        d01_payload,
        cf4_provenance=sources["cf4"],
        d01_provenance=sources["d01"],
    )
    return evaluate_d1_l3_proof_ledger(
        evidence,
        tick_id="M-D1-L3-LEDGER",
        sources=sources,
        generated=generated or date.today().isoformat(),
    )


def main() -> int:
    today = date.today().isoformat()
    ledger = build_ledger(generated=today)

    out_path = SCI_FLOW / f"M-D1-L3_proof_ledger_{today}.json"
    out_path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")

    cf4_payload, d01_payload, sources = load_d1_l3_ledger_artifacts(SCI_FLOW)
    evidence = build_d1_l3_evidence_from_artifacts(
        cf4_payload,
        d01_payload,
        cf4_provenance=sources["cf4"],
        d01_provenance=sources["d01"],
    )
    print(render_proof_report(evaluate_eia_proof_version(evidence)))
    print(json.dumps(ledger, indent=2))
    print(f"wrote {out_path}")
    return 0 if ledger["e_endo_support"] == "partial" and not ledger["claim_allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
