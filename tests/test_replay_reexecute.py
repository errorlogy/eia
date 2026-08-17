"""Tests for deterministic trace re-execution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from eia.audit import CausalTrace, TraceNodeKind
from eia.audit.replay import (
    ReplayMetadataError,
    compare_traces,
    re_execute_trace,
    trace_fingerprint,
)
from eia.pipeline import run_scenario

SCENARIO = Path(__file__).resolve().parents[1] / "scenarios" / "twin_world_001.yaml"


def test_replay_reexecute_matches_original(tmp_path: Path) -> None:
    """Re-executing a trace with metadata should produce a matching fingerprint."""
    result = run_scenario(SCENARIO, traces_dir=tmp_path)
    original_path = result["trace_path"]
    assert original_path.exists()
    assert result["loop"].trace.metadata is not None

    comparison = re_execute_trace(original_path, traces_dir=tmp_path / "replay")
    assert comparison.matched is True
    assert comparison.fingerprint_match is True
    assert comparison.eoi_match is True
    assert comparison.auth_match is True
    assert comparison.eoi_original == pytest.approx(result["twin_result"].eoi)
    assert comparison.auth_original["is_authentic"] == result["authentic_verdict"].is_authentic


def test_seed_determinism_same_fingerprint(tmp_path: Path) -> None:
    """Two runs with the same seed must yield identical trace fingerprints."""
    r1 = run_scenario(SCENARIO, traces_dir=tmp_path / "a", seed=12345)
    r2 = run_scenario(SCENARIO, traces_dir=tmp_path / "b", seed=12345)

    fp1 = trace_fingerprint(r1["loop"].trace)
    fp2 = trace_fingerprint(r2["loop"].trace)
    assert fp1 == fp2
    assert r1["twin_result"].eoi == r2["twin_result"].eoi


def test_mismatch_detection_different_seed(tmp_path: Path) -> None:
    """Different seeds should produce detectable mismatches."""
    original = run_scenario(SCENARIO, traces_dir=tmp_path, seed=100)
    replay_result = run_scenario(SCENARIO, traces_dir=tmp_path / "other", seed=999)

    comparison = compare_traces(original["loop"].trace, replay_result["loop"].trace)
    assert comparison.matched is False
    assert comparison.fingerprint_match is False or not comparison.eoi_match


def test_missing_metadata_raises_helpful_error(tmp_path: Path) -> None:
    """Legacy traces without metadata should fail with a helpful message."""
    legacy_path = tmp_path / "legacy.jsonl"
    trace = CausalTrace("legacy-no-meta")
    trace.add_node(TraceNodeKind.OBSERVATION_INGEST, {"id": "o1", "topic": "test"})
    trace.export_jsonl(legacy_path)

    loaded = CausalTrace.load_jsonl(legacy_path)
    assert loaded.metadata is None

    with pytest.raises(ReplayMetadataError, match="before replay metadata"):
        re_execute_trace(legacy_path)


def test_legacy_header_without_metadata_field(tmp_path: Path) -> None:
    """Old-style header line without metadata block is rejected on re-execute."""
    legacy_path = tmp_path / "old-header.jsonl"
    with legacy_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"trace_id": "trace-old", "type": "header"}) + "\n")
        f.write(
            json.dumps(
                {
                    "type": "node",
                    "id": "n1",
                    "kind": "eoi_score",
                    "timestamp": "2026-08-17T09:00:00Z",
                    "payload": {"eoi": 0.5},
                }
            )
            + "\n"
        )

    with pytest.raises(ReplayMetadataError):
        re_execute_trace(legacy_path)
