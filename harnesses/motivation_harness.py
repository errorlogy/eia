"""Motivation harness — stress tests for drive dynamics."""

from __future__ import annotations

from eia.beliefs import BeliefField
from eia.drives import DriveEngine
from eia.schemas.belief import BeliefKind


def run_saturation_test(ticks: int = 20) -> dict:
    """Verify drives saturate rather than runaway."""
    field = BeliefField()
    field.upsert_belief(
        "b1",
        kind=BeliefKind.CATEGORICAL,
        subject="test",
        claim="high entropy",
        distribution={"a": 0.33, "b": 0.33, "c": 0.34},
        uncertainty=0.9,
    )
    engine = DriveEngine()
    intensities: list[float] = []
    for _ in range(ticks):
        mot = engine.compute(field)
        top = max(s.intensity for s in mot.signals)
        intensities.append(top)
    return {
        "max_intensity": max(intensities),
        "final_intensity": intensities[-1],
        "saturated": intensities[-1] < 0.95,
        "series": intensities,
    }


def run_decay_test() -> dict:
    """After satisfaction, drives should decay."""
    field = BeliefField()
    field.upsert_belief(
        "b1",
        kind=BeliefKind.CATEGORICAL,
        subject="test",
        claim="resolved",
        distribution={"resolved": 1.0},
        uncertainty=0.05,
    )
    engine = DriveEngine()
    engine.state.epistemic = 0.8
    mot = engine.compute(field, satisfaction={__import__("eia.schemas.motivation", fromlist=["DriveKind"]).DriveKind.EPISTEMIC: 0.5})
    return {"epistemic_after_satisfaction": mot.signals[0].intensity}


if __name__ == "__main__":
    sat = run_saturation_test()
    dec = run_decay_test()
    print("Saturation test:", sat["saturated"], "max=", sat["max_intensity"])
    print("Decay test: epistemic=", dec["epistemic_after_satisfaction"])
