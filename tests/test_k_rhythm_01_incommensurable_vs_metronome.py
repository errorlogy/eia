"""Smoke tests for K-RHYTHM-01 rhythm substrate harness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HARNESS_DIR = REPO / "research" / "brain_ai" / "harnesses"

if str(HARNESS_DIR) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIR))

_H = HARNESS_DIR / "k_rhythm_01_incommensurable_vs_metronome.py"
_spec = importlib.util.spec_from_file_location("k_rhythm_01_test", _H)
assert _spec and _spec.loader
_h = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _h
_spec.loader.exec_module(_h)


def test_tier_c_invariants():
    payload = _h.build_k_rhythm_01_payload(seed=42, generated="2026-09-30", t_end=30.0)
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["agi_star_claim"] is False
    assert payload["theory_strand"] == "kairologos_explore"
    assert payload["ceiling"] == "C2"
    assert payload["sigma_external"] == 0.0


def test_arms_and_metrics():
    payload = _h.build_k_rhythm_01_payload(seed=42, generated="2026-09-30", t_end=30.0)
    arms = payload["arms"]
    assert "coupled_incommensurable" in arms
    assert "metronome_single_freq" in arms
    for key in arms:
        assert arms[key]["periodicity_score"] >= 0.0
        assert arms[key]["sequence_novelty"] >= 0.0


def test_contrast_direction_smoke():
    payload = _h.build_k_rhythm_01_payload(seed=42, generated="2026-09-30", t_end=60.0)
    assert payload["contrast_verdict"]["coupled_more_novel"] is True
    assert payload["diagnostic_pass"] is True


def test_falsifiers_structure():
    payload = _h.build_k_rhythm_01_payload(seed=42, generated="2026-09-30", t_end=30.0)
    fals = payload["falsifiers"]
    assert "F-METRONOME-NOVELTY-PARITY" in fals
    assert "F-RHYTHM-AS-E" in fals


def test_artifact_sha256_stable():
    p1 = _h.build_k_rhythm_01_payload(seed=42, generated="2026-09-30", t_end=30.0)
    p2 = _h.build_k_rhythm_01_payload(seed=42, generated="2026-09-30", t_end=30.0)
    assert _h.artifact_sha256(p1) == _h.artifact_sha256(p2)
