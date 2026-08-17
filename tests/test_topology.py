"""Tests for SourceMass topology on causal traces."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from eia.audit import CausalTrace, TraceNodeKind
from eia.audit.topology import CausalTraceTopology
from eia.pipeline import run_scenario

SCENARIO = Path(__file__).resolve().parents[1] / "scenarios" / "twin_world_001.yaml"


def test_topology_on_twin_world_trace() -> None:
    result = run_scenario(SCENARIO, traces_dir=Path("traces/test_topology"))
    metrics = CausalTraceTopology(result["loop"].trace).measure_initiative()
    assert metrics is not None
    sm = metrics.source_mass
    assert sm.internal + sm.ambient + sm.user_request == pytest.approx(1.0, abs=0.01)
    assert sm.request_independence >= 0.0


def test_authentic_reason_includes_topology() -> None:
    result = run_scenario(SCENARIO, traces_dir=Path("traces/test_topology"))
    auth = result["authentic_verdict"]
    assert auth.topology is not None
    assert "request_independence" in auth.topology
    assert auth.source_mass_independent is not None


def test_source_mass_root_classification() -> None:
    trace = CausalTrace("topo-test")
    trace.add_node(
        TraceNodeKind.OBSERVATION_INGEST,
        {"id": "obs-user", "is_user_trigger": True, "source": "user_message"},
    )
    trace.add_node(
        TraceNodeKind.MOTIVE_FORMATION,
        {"id": "mot-1"},
        parent_kind=TraceNodeKind.OBSERVATION_INGEST,
    )
    trace.add_node(
        TraceNodeKind.INTENTION_GENESIS,
        {"id": "int-1", "abstained": False},
        parent_kind=TraceNodeKind.MOTIVE_FORMATION,
    )
    metrics = CausalTraceTopology(trace).measure("int-1")
    assert metrics.source_mass.user_request > 0.5
