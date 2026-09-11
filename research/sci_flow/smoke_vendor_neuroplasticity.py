#!/usr/bin/env python3
"""Minimal smoke test for research/vendor neuroplasticity packages. No LLM calls."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
NEURAXON = REPO / "research" / "vendor" / "neuraxon"
GRAPHITTI = REPO / "research" / "vendor" / "graphitti"


def smoke_neuraxon() -> None:
    sys.path.insert(0, str(NEURAXON))
    from neuraxon2 import NeuraxonNetwork, NetworkParameters  # noqa: WPS433

    params = NetworkParameters(
        num_input_neurons=3,
        num_hidden_neurons=5,
        num_output_neurons=2,
    )
    net = NeuraxonNetwork(params)
    for _ in range(10):
        net.simulate_step()
    assert net.step_count == 10
    print("neuraxon: OK", net.step_count, net.time)


def smoke_graphitti_tree() -> None:
    required = [
        GRAPHITTI / "CMakeLists.txt",
        GRAPHITTI / "configfiles" / "test-tiny.xml",
        GRAPHITTI / "docs" / "User" / "configuration.md",
    ]
    missing = [p for p in required if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"graphitti tree incomplete: {missing}")
    cfg = (GRAPHITTI / "configfiles" / "test-tiny.xml").read_text(encoding="utf-8")
    if "ConnGrowth" not in cfg:
        raise ValueError("test-tiny.xml missing ConnGrowth")
    print("graphitti: OK (tree + ConnGrowth config)")


def main() -> int:
    smoke_neuraxon()
    smoke_graphitti_tree()
    print("smoke_vendor_neuroplasticity: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
