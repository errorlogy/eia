"""Tests for T-BRAIN-05 connectome source parity harness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRAIN_AI = REPO / "research" / "brain_ai"
HARNESS_DIR = BRAIN_AI / "harnesses"
ADAPTERS = BRAIN_AI / "adapters"

for path in (str(HARNESS_DIR), str(ADAPTERS)):
    if path not in sys.path:
        sys.path.insert(0, path)

_HARNESS = HARNESS_DIR / "t_brain_05_connectome_parity.py"
_spec = importlib.util.spec_from_file_location("t_brain_05_connectome_parity_test", _HARNESS)
assert _spec and _spec.loader
_harness = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _harness
_spec.loader.exec_module(_harness)


def test_build_payload_tier_c_invariants():
    payload = _harness.build_t_brain_05_payload(seed=42, prefer_brian2=False)
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["agi_star_claim"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["harness_id"] == "T-BRAIN-05"
    assert payload["x_trigger_zero"] is True
    assert len(payload["per_source"]) == 4


def test_all_sources_valid_omega():
    payload = _harness.build_t_brain_05_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    for key, src in payload["per_source"].items():
        omega = float(src["omega_t"])
        assert 0.0 <= omega <= 1.0, f"{key} omega out of range: {omega}"


def test_omega_span_measurable():
    payload = _harness.build_t_brain_05_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    assert payload["aggregate_metrics"]["omega_span"] >= _harness.OMEGA_SPAN_MIN


def test_source_fallback_flags_present():
    payload = _harness.build_t_brain_05_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    for key, src in payload["per_source"].items():
        fb = src["source_fallback"]
        assert "fallback" in fb
        assert "mode" in fb
        if key == "synthetic":
            assert fb["fallback"] is False


def test_f_source_parity_structural_diversity():
    payload = _harness.build_t_brain_05_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    assert payload["aggregate_metrics"]["structural_fingerprints_unique"] > 1
    assert payload["f_source_parity"]["status"] == "confirmed"


def test_genesis_delta_when_shadow_included():
    payload = _harness.build_t_brain_05_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10", include_shadow=True
    )
    for src in payload["per_source"].values():
        assert src["genesis_delta"] == 1.0
        assert src["has_novel_g_prime"] is True


def test_diagnostic_pass():
    payload = _harness.build_t_brain_05_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    assert payload["diagnostic_pass"] is True


def test_artifact_sha256_stable():
    p1 = _harness.build_t_brain_05_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    p2 = _harness.build_t_brain_05_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    assert _harness.artifact_sha256(p1) == _harness.artifact_sha256(p2)


def test_build_spec_status_implemented():
    spec = _harness.build_t_brain_05_spec()
    assert spec["status"] == "implemented"
    assert spec["harness_id"] == "T-BRAIN-05"


def test_render_markdown_contains_invariants():
    payload = _harness.build_t_brain_05_payload(
        seed=42, prefer_brian2=False, generated="2026-09-10"
    )
    payload["artifact_sha256"] = _harness.artifact_sha256(payload)
    md = _harness.render_t_brain_05_markdown(payload)
    assert "claim_allowed=false" in md
    assert "M-T-BRAIN-05" in md
    assert "F-SOURCE-PARITY" in md
