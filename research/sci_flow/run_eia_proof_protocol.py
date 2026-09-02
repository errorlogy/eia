"""CLI smoke for EIA proof protocol v0.1.

Runs a tiny deterministic proof-version example for sci-flow logs. It does not
execute live actions, does not call LLMs, and never raises AGI* / C-ladder claims.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "cursor-starter-v0.2" / "src"
sys.path.insert(0, str(_SRC))

from eia.evidence_proofs import EvidenceItem, evaluate_eia_proof_version, render_proof_report


def main() -> int:
    item = EvidenceItem(
        evidence_id="M-CF4-reference",
        metric_id="CF4_E_PARTIAL",
        value=0.95,
        trajectory_changed=True,
        do_z_changes_g_distribution=True,
        x_non_triggering=True,
        matching_external_initiating_signal=False,
        falsifiers_triggered=(),
        provenance="research/sci_flow/M-CF4_metrics_2026-08-20.md",
    )
    proof = evaluate_eia_proof_version((item,))
    print(render_proof_report(proof))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
