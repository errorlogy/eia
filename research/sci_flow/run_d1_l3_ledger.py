"""D1×L3 empirical proof ledger — CF-4 + D01 → EvidenceItem batch.

Writes dated JSON artifact for cell_registry D1.L3. Tier 0: no LLM, no AGI*.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from datetime import date
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "cursor-starter-v0.2" / "src"
_WOE_PKG = _SRC / "eia"
SCI_FLOW = Path(__file__).resolve().parent


def _load_evidence_proofs():
    """Load research-branch evidence_proofs without shadowing main ``eia``."""
    pkg_name = "woe_eia_ledger"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [str(_WOE_PKG)]  # type: ignore[attr-defined]
        sys.modules[pkg_name] = pkg

    full = f"{pkg_name}.evidence_proofs"
    if full in sys.modules:
        return sys.modules[full]

    path = _WOE_PKG / "evidence_proofs.py"
    spec = importlib.util.spec_from_file_location(full, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load evidence_proofs from {path}")
    module = importlib.util.module_from_spec(spec)
    module.__package__ = pkg_name
    sys.modules[full] = module
    spec.loader.exec_module(module)
    return module


_ep = _load_evidence_proofs()
build_d1_l3_evidence_from_artifacts = _ep.build_d1_l3_evidence_from_artifacts
evaluate_d1_l3_proof_ledger = _ep.evaluate_d1_l3_proof_ledger
evaluate_eia_proof_version = _ep.evaluate_eia_proof_version
load_d1_l3_ledger_artifacts = _ep.load_d1_l3_ledger_artifacts
render_proof_report = _ep.render_proof_report


def build_ledger(
    sci_flow_dir: Path = SCI_FLOW,
    *,
    generated: str | None = None,
    d01_name: str | None = "M-D01_EOI_k_metrics_2026-09-01.json",
    d01_do_z_name: str | None = None,
) -> dict:
    """Build D1×L3 ledger dict from on-disk CF-4 and D01 artifacts."""
    cf4_payload, d01_payload, sources, d01_do_z_payload = load_d1_l3_ledger_artifacts(
        sci_flow_dir,
        d01_name=d01_name,
        d01_do_z_name=d01_do_z_name,
    )
    evidence = build_d1_l3_evidence_from_artifacts(
        cf4_payload,
        d01_payload,
        cf4_provenance=sources["cf4"],
        d01_provenance=sources["d01"],
        d01_do_z_payload=d01_do_z_payload,
        d01_do_z_provenance=sources.get("d01_do_z"),
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

    cf4_payload, d01_payload, sources, d01_do_z_payload = load_d1_l3_ledger_artifacts(SCI_FLOW)
    evidence = build_d1_l3_evidence_from_artifacts(
        cf4_payload,
        d01_payload,
        cf4_provenance=sources["cf4"],
        d01_provenance=sources["d01"],
        d01_do_z_payload=d01_do_z_payload,
        d01_do_z_provenance=sources.get("d01_do_z"),
    )
    print(render_proof_report(evaluate_eia_proof_version(evidence)))
    print(json.dumps(ledger, indent=2))
    print(f"wrote {out_path}")
    return 0 if ledger["e_endo_support"] == "partial" and not ledger["claim_allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
