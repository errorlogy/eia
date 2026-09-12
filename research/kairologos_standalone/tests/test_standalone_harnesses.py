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
from t_kai_09_attention_vs_diffusion import run_experiment as run_t_kai_09
from t_kai_10_nd_quasi_orthogonality import run_experiment as run_t_kai_10
from t_kai_11_topo_viz import run_experiment as run_t_kai_11
from lemma_battery import run_lemma_battery


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


def test_t_kai_09_attention_vs_diffusion():
    payload = run_t_kai_09(seed=7)
    assert payload["harness_id"] == "T-KAI-09"
    assert "eight_node_task" in payload
    assert "lemma_results" in payload


def test_t_kai_10_nd_quasi_orthogonality():
    payload = run_t_kai_10(seed=7)
    assert payload["harness_id"] == "T-KAI-10"
    assert payload["quasi_orthogonality"]["max_abs_cosine"] < 0.2


def test_t_kai_11_topo_viz_export():
    payload = run_t_kai_11()
    assert payload["harness_id"] == "T-KAI-11"
    assert payload["schema_validation"]["pass"] is True
    assert payload["export_count"] >= 3
    assert "if_then_else" in payload["exported_programs"]
    assert payload["execution_path"][0] == "input_x"
    assert payload["execution_path"][-1] == "braid_merge"


def test_pre_proof_lemma_battery():
    payload = run_lemma_battery(seed=7)
    assert payload["summary"]["total"] == 6
    assert payload["summary"]["passed"] >= 4


def test_no_eia_fields_in_payload():
    payload = run_klein(seed=1)
    blob = json.dumps(payload)
    assert "claim_allowed" not in blob
    assert "tier" not in blob or payload.get("tier") is None
