#!/usr/bin/env python3
"""Run full PRE_PROOF lemma battery + individual T-KAI harnesses."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from harnesses.lemma_battery import main as run_battery
from harnesses.t_kai_08_syntax_vs_semantics import main as run_t08
from harnesses.t_kai_09_attention_vs_diffusion import main as run_t09
from harnesses.t_kai_10_nd_quasi_orthogonality import main as run_t10


def main() -> None:
    print("=== T-KAI-08 ===")
    run_t08()
    print("=== T-KAI-09 ===")
    run_t09()
    print("=== T-KAI-10 ===")
    run_t10()
    print("=== PRE_PROOF lemma battery ===")
    payload = run_battery()
    s = payload["summary"]
    print(f"Done: {s['passed']}/{s['total']} lemmas passed")


if __name__ == "__main__":
    main()
