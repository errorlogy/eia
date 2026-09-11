"""Tests for T-BRAIN-01 connectome→O_t harness (graceful Brian2 skip)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRAIN_AI = REPO / "research" / "brain_ai"
HARNESS_DIR = BRAIN_AI / "harnesses"
ADAPTERS = BRAIN_AI / "adapters"

for path in (str(HARNESS_DIR), str(ADAPTERS)):
    if path not in sys.path:
        sys.path.insert(0, path)

_HARNESS = HARNESS_DIR / "t_brain_01_connectome_ot.py"
_spec = importlib.util.spec_from_file_location("t_brain_01_connectome_ot_test", _HARNESS)
assert _spec and _spec.loader
_harness = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _harness
_spec.loader.exec_module(_harness)


def test_build_payload_tier_c_invariants():
    payload = _harness.build_t_brain_01_payload(seed=42, prefer_brian2=False)
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["agi_star_claim"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["harness_id"] == "T-BRAIN-01"
    assert payload["milestone"] == "M-BRAIN-AI"
    assert isinstance(payload.get("omega_t"), float)
    assert 0.0 <= payload["omega_t"] <= 1.0


def test_spike_backend_fallback_without_brian2():
    payload = _harness.build_t_brain_01_payload(seed=7, prefer_brian2=False)
    spike = payload["spike_dynamics"]
    assert spike["backend"] == "synthetic_spike_trains"
    assert spike["n_spikes"] >= 0


def test_artifact_sha256_stable():
    p1 = _harness.build_t_brain_01_payload(seed=42, prefer_brian2=False, generated="2026-09-09")
    p2 = _harness.build_t_brain_01_payload(seed=42, prefer_brian2=False, generated="2026-09-09")
    s1 = _harness.artifact_sha256(p1)
    s2 = _harness.artifact_sha256(p2)
    assert s1 == s2
    assert len(s1) == 64


def test_connectome_subgraph_loads():
    from connectome_export import load_subgraph

    sg = load_subgraph(seed=1)
    assert sg.n_nodes >= 4
    assert len(sg.adjacency) == sg.n_nodes


def test_google_male_cns_fallback_when_data_absent():
    from connectome_export import load_subgraph

    sg = load_subgraph(connectome_source="google_male_cns", seed=11, n_nodes=12)
    assert "google_male_cns" in sg.source
    assert sg.n_nodes == 12


def test_export_google_male_subgraph_stub():
    import tempfile
    from connectome_export import export_google_male_subgraph

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "male_stub.json"
        payload = export_google_male_subgraph(out, seed=5, n_nodes=16)
        assert payload["source"] == "google_male_cns_stub"
        assert out.is_file()


def test_ot_injection_produces_omega_wave_state():
    from connectome_export import load_subgraph
    from brian2_lif_subgraph import synthetic_spike_trains
    from ot_injection import inject_omega_from_spikes

    sg = load_subgraph(seed=3)
    spikes = synthetic_spike_trains(sg, seed=3)
    ctx = inject_omega_from_spikes(spikes, sg.node_ids)
    assert "omega_wave_state" in ctx
    assert ctx["crosswalk"]["connectome_spike_phases_to_omega_wave_state"] is True


def test_render_markdown_contains_invariants():
    payload = _harness.build_t_brain_01_payload(seed=42, prefer_brian2=False, generated="2026-09-09")
    payload["artifact_sha256"] = _harness.artifact_sha256(payload)
    md = _harness.render_t_brain_01_markdown(payload)
    assert "claim_allowed=false" in md
    assert "M-T-BRAIN-01" in md
