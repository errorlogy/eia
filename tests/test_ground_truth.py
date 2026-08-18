"""Tests for ground-truth loading and scoring."""

from __future__ import annotations

from pathlib import Path

from eia.experiment.baseline import BaselineCondition
from eia.pipeline import run_scenario
from eia.scenarios import load_ground_truth, score_initiative_against_label

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIO = ROOT / "scenarios" / "twin_world_001.yaml"


def test_load_ground_truth_twin_world_001() -> None:
    gt = load_ground_truth(DEFAULT_SCENARIO)
    assert gt is not None
    assert len(gt["initiatives"]) >= 1
    assert gt["initiatives"][0]["expected_kind"] == "ask"
    assert gt["initiatives"][0]["target"] == "belief-deadline"


def test_score_initiative_full_eia_precision() -> None:
    gt = load_ground_truth(DEFAULT_SCENARIO)
    label = gt["initiatives"][0]
    run = run_scenario(
        DEFAULT_SCENARIO,
        traces_dir=Path("traces/test_ground_truth"),
        baseline=BaselineCondition.FULL_EIA,
    )
    score = score_initiative_against_label(run, label)
    assert score["kind_match"] is True
    assert score["precision_hit"] is True


def test_score_initiative_reactive_misses() -> None:
    gt = load_ground_truth(DEFAULT_SCENARIO)
    label = gt["initiatives"][0]
    run = run_scenario(
        DEFAULT_SCENARIO,
        traces_dir=Path("traces/test_ground_truth"),
        baseline=BaselineCondition.REACTIVE_ONLY,
    )
    score = score_initiative_against_label(run, label)
    assert score["precision_hit"] is False
