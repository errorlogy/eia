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
from t_kai_08_syntax_vs_semantics import run_experiment as run_t_kai_08


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


def test_topo_parser_and_interpreter():
    topo_root = ROOT / "topo_lang"
    sys.path.insert(0, str(topo_root))
    from parser import load_topo  # noqa: E402
    from interpreter import TopoInterpreter  # noqa: E402

    program = load_topo(topo_root / "examples" / "if_then_else.topo")
    trace = TopoInterpreter(program).execute()
    assert trace.path[0] == "input_x"
    assert trace.path[-1] == "braid_merge"
    assert len(trace.path) >= 3


def test_t_kai_08_syntax_vs_semantics():
    payload = run_t_kai_08(seed=7)
    assert payload["harness_id"] == "T-KAI-08"
    assert len(payload["tasks"]) == 5
    agg = payload["aggregate"]
    assert agg["mean_topological_shuffle_similarity"] >= agg["mean_linear_shuffle_similarity"]


def test_no_eia_fields_in_payload():
    payload = run_klein(seed=1)
    blob = json.dumps(payload)
    assert "claim_allowed" not in blob
    assert "tier" not in blob or payload.get("tier") is None
