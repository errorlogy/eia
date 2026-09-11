"""Tests for K-KUR-01 Kuramoto×OMEGA×genesis harness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HARNESS_DIR = REPO / "research" / "brain_ai" / "harnesses"
ADAPTERS = REPO / "research" / "brain_ai" / "adapters"

for path in (str(HARNESS_DIR), str(ADAPTERS)):
    if path not in sys.path:
        sys.path.insert(0, path)

_H = HARNESS_DIR / "k_kur_01_kuramoto_omega_genesis.py"
_spec = importlib.util.spec_from_file_location("k_kur_01_test", _H)
assert _spec and _spec.loader
_h = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _h
_spec.loader.exec_module(_h)


def test_tier_c_invariants():
    payload = _h.build_k_kur_01_payload(
        seed=42, generated="2026-09-11", sources=("bundled_tiny",)
    )
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["agi_star_claim"] is False
    assert payload["theory_strand"] == "kairologos_explore"
    assert payload["ceiling"] == "C2"


def test_correlations_present():
    payload = _h.build_k_kur_01_payload(
        seed=42, generated="2026-09-11", sources=("bundled_tiny",)
    )
    corr = payload["correlation"]
    assert corr["kuramoto_span"] > 0.0
    assert corr["omega_span"] > 0.0
    assert corr["r_kuramoto_omega"] is not None


def test_falsifiers_structure():
    payload = _h.build_k_kur_01_payload(
        seed=42, generated="2026-09-11", sources=("bundled_tiny",)
    )
    fals = payload["falsifiers"]
    assert "F-KURAMOTO-AS-E" in fals
    assert "F-OMEGA-DECOR" in fals


def test_diagnostic_pass_bundled():
    payload = _h.build_k_kur_01_payload(
        seed=42, generated="2026-09-11", sources=("bundled_tiny",)
    )
    assert payload["diagnostic_pass"] is True


def test_artifact_sha256_stable():
    p1 = _h.build_k_kur_01_payload(seed=42, generated="2026-09-11", sources=("bundled_tiny",))
    p2 = _h.build_k_kur_01_payload(seed=42, generated="2026-09-11", sources=("bundled_tiny",))
    assert _h.artifact_sha256(p1) == _h.artifact_sha256(p2)
