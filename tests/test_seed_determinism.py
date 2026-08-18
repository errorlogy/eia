"""Multi-seed determinism tests for twin_world_001 (Loop 28)."""

from __future__ import annotations

from pathlib import Path

from eia.audit.replay import trace_fingerprint
from eia.pipeline import run_scenario

SCENARIO = Path(__file__).resolve().parents[1] / "scenarios" / "twin_world_001.yaml"
BOOTSTRAP_SEEDS = (42, 123, 999)


def test_same_seed_yields_identical_fingerprint(tmp_path: Path) -> None:
    """Each seed must produce identical fingerprints across two independent runs."""
    for seed in BOOTSTRAP_SEEDS:
        r1 = run_scenario(SCENARIO, traces_dir=tmp_path / f"a-{seed}", seed=seed)
        r2 = run_scenario(SCENARIO, traces_dir=tmp_path / f"b-{seed}", seed=seed)

        fp1 = trace_fingerprint(r1["loop"].trace)
        fp2 = trace_fingerprint(r2["loop"].trace)
        assert fp1 == fp2, f"seed {seed}: fingerprints differ within seed"
        assert r1["twin_result"].eoi == r2["twin_result"].eoi


def test_different_seeds_yield_distinct_fingerprints(tmp_path: Path) -> None:
    """Bootstrap seeds must produce distinct trace fingerprints."""
    fingerprints: dict[int, str] = {}
    for seed in BOOTSTRAP_SEEDS:
        result = run_scenario(SCENARIO, traces_dir=tmp_path / str(seed), seed=seed)
        fingerprints[seed] = trace_fingerprint(result["loop"].trace)

    unique = set(fingerprints.values())
    assert len(unique) == len(BOOTSTRAP_SEEDS), (
        f"expected {len(BOOTSTRAP_SEEDS)} distinct fingerprints, got {len(unique)}: "
        f"{fingerprints}"
    )
