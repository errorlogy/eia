"""Tests for K-KUR-02 paired do(O) scramble harness."""

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

_H = HARNESS_DIR / "k_kur_02_scramble_decorrelation.py"
_spec = importlib.util.spec_from_file_location("k_kur_02_test", _H)
assert _spec and _spec.loader
_h = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _h
_spec.loader.exec_module(_h)


def test_tier_c_invariants():
    payload = _h.build_k_kur_02_payload(
        seed=42, generated="2026-09-11", sources=("bundled_tiny",)
    )
    assert payload["tier"] == "C"
    assert payload["claim_allowed"] is False
    assert payload["e_endo_support"] == "none"
    assert payload["theory_strand"] == "kairologos_explore"


def test_paired_arms_present():
    payload = _h.build_k_kur_02_payload(
        seed=42, generated="2026-09-11", sources=("bundled_tiny",)
    )
    assert payload["paired_arms"] == ["coupled_active", "phase_scramble_control"]


def test_scramble_verdict_present():
    payload = _h.build_k_kur_02_payload(
        seed=42, generated="2026-09-11", sources=("bundled_tiny",)
    )
    assert "F-KURAMOTO-AS-E" in payload["scramble_verdict"]


def test_genesis_invariant_under_scramble():
    payload = _h.build_k_kur_02_payload(
        seed=42, generated="2026-09-11", sources=("bundled_tiny",)
    )
    assert payload["scramble_verdict"]["genesis_invariant_under_scramble"] is True


def test_diagnostic_pass_bundled():
    payload = _h.build_k_kur_02_payload(
        seed=42, generated="2026-09-11", sources=("bundled_tiny",)
    )
    assert payload["diagnostic_pass"] is True
