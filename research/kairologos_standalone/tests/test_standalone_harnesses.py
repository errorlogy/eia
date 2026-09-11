"""Smoke tests for Kairologos standalone harnesses."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "harnesses"))

from t_kai_01_kuramoto_phase import run_experiment as run_kuramoto
from t_kai_02_hdc_binding_capacity import run_experiment as run_hdc
from t_kai_05_klein_involution import run_experiment as run_klein
from t_kai_06_padic_clustering import run_experiment as run_padic


def test_kuramoto_finds_sync_at_high_coupling():
    payload = run_kuramoto(seed=7)
    gamma = payload["per_carrier"]["gamma_42hz"]
    assert gamma["high_k_snapshot"]["mean_r"] > 0.75


def test_hdc_capacity_non_trivial():
    payload = run_hdc(seed=7)
    assert payload["estimated_capacity_pairs"] >= 12


def test_klein_involution():
    payload = run_klein(seed=7)
    assert payload["statistics"]["min_fidelity_k_squared"] > 0.999


def test_padic_ultrametric():
    payload = run_padic()
    assert payload["ultrametric_holds"] is True


def test_no_eia_fields_in_payload():
    payload = run_klein(seed=1)
    blob = json.dumps(payload)
    assert "claim_allowed" not in blob
    assert "tier" not in blob or payload.get("tier") is None
