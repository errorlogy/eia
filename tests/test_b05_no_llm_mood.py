"""Tests for M-B05 no-LLM-mood structural harness (Tier 0)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAIN_SRC = REPO / "src"
SCI_FLOW = REPO / "research" / "sci_flow"

if str(MAIN_SRC) not in sys.path:
    sys.path.insert(0, str(MAIN_SRC))
if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from b05_no_llm_mood_harness import (  # noqa: E402
    drive_intensities,
    mock_llm_mood_proxy,
    run_b05_batch,
    _field_baseline,
    _field_high_coherence,
    _field_high_epistemic,
)

_RUN = SCI_FLOW / "run_b05_no_llm_mood.py"
_spec = importlib.util.spec_from_file_location("run_b05_no_llm_mood", _RUN)
assert _spec and _spec.loader
_runner = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _runner
_spec.loader.exec_module(_runner)


def test_b05_batch_passes() -> None:
    result = run_b05_batch(REPO)
    assert result.claim_allowed is False
    assert result.tier == "0"
    assert result.cube_cell == "D1×L1"
    assert result.passed is True
    assert all(c.ok for c in result.checks)


def test_same_mood_different_gradients_different_drives() -> None:
    fa = _field_high_epistemic()
    fb = _field_high_coherence()
    assert mock_llm_mood_proxy(fa) == mock_llm_mood_proxy(fb)
    assert fa.gradient_snapshot() != fb.gradient_snapshot()
    assert drive_intensities(fa) != drive_intensities(fb)


def test_mood_proxy_mutation_does_not_change_drives() -> None:
    field = _field_baseline()
    before = drive_intensities(field)
    for belief in field.beliefs.values():
        belief.metadata["mood_proxy"] = [0.99, 0.01, 0.5]
    assert drive_intensities(field) == before


def test_runner_artifact_stem() -> None:
    assert _runner.ARTIFACT_STEM == "M-B05_no_llm_mood_2026-09-02"
