"""Command-line entry points for the reference experiments."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .causal import EndogeneityEstimator
from .emergence import (
    EmergenceConfig,
    EndogenousEmergenceSimulator,
    compact_run_dict,
)
from .metrics import summarize
from .models import InitiativeProposal
from .simulator import SimulationRunner, load_scenario


def _proposal_dict(proposal: InitiativeProposal | None) -> dict[str, object] | None:
    if proposal is None:
        return None
    return {
        "proposal_id": proposal.proposal_id,
        "kind": proposal.kind.value,
        "motive": proposal.motive.value,
        "target": proposal.target,
        "content": proposal.content,
    }


def _default_scenario() -> Path:
    return Path(__file__).resolve().parents[2] / "examples" / "autonomous_question.json"


def run_demo(path: Path) -> int:
    scenario = load_scenario(path)
    simulation = SimulationRunner().run(scenario)
    payload = {
        "scenario": scenario.name,
        "selected": [_proposal_dict(item.selected) for item in simulation.results],
        "metrics": asdict(summarize(simulation.results)),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0


def run_eoi_demo(path: Path, trials: int) -> int:
    scenario = load_scenario(path)
    runner = SimulationRunner()
    factual = runner.run(scenario)
    observed = next(
        (item.selected for item in factual.results if item.selected is not None),
        None,
    )
    if observed is None:
        raise RuntimeError("scenario produced no initiative")

    def twin(remove_user_events: bool, seed: int) -> InitiativeProposal | None:
        del seed  # Reference runtime is deterministic; stochastic adapters may use it.
        result = runner.run(scenario, remove_user_events=remove_user_events)
        return next((item.selected for item in result.results if item.selected is not None), None)

    estimate = EndogeneityEstimator().estimate(observed, twin, trials=trials)
    print(json.dumps(asdict(estimate), ensure_ascii=False, indent=2, default=str))
    return 0


def run_woe_demo(*, frequency_hz: float, duration_seconds: float, seed: int) -> int:
    config = EmergenceConfig(
        nominal_frequency_hz=frequency_hz,
        duration_seconds=duration_seconds,
    )
    simulator = EndogenousEmergenceSimulator()
    factual = simulator.run(config, seed=seed)
    no_world_model = simulator.run(config, seed=seed, world_model_enabled=False)
    phase_scrambled = simulator.run(config, seed=seed, scramble_phases=True)
    carrier_sweep: dict[str, dict[str, object]] = {}
    for carrier in (20.0, 30.0, 42.0, 70.0):
        run = simulator.run(
            EmergenceConfig(
                nominal_frequency_hz=carrier,
                duration_seconds=duration_seconds,
            ),
            seed=seed,
        )
        carrier_sweep[str(carrier)] = {
            "emerged": run.intent is not None,
            "target": run.intent.target_id if run.intent else None,
            "emerged_at_seconds": run.intent.emerged_at_seconds if run.intent else None,
        }
    payload = {
        "experiment": "EIA Window of Emergence shadow simulation",
        "factual": compact_run_dict(factual),
        "negative_controls": {
            "zero_world_model_tension_emerged": no_world_model.intent is not None,
            "phase_scrambling_emerged": phase_scrambled.intent is not None,
        },
        "carrier_frequency_sweep": carrier_sweep,
        "claim_boundary": (
            "Operational evidence for state-dependent initiative formation only; "
            "not evidence of consciousness, free will or biological gamma activity."
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="eia")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="run the autonomous-question scenario")
    demo.add_argument("--scenario", type=Path, default=_default_scenario())
    eoi = subparsers.add_parser("eoi-demo", help="run counterfactual EOI estimation")
    eoi.add_argument("--scenario", type=Path, default=_default_scenario())
    eoi.add_argument("--trials", type=int, default=64)
    scenario = subparsers.add_parser("run-scenario", help="run a JSON scenario")
    scenario.add_argument("path", type=Path)
    woe = subparsers.add_parser("woe-demo", help="run the Window-of-Emergence experiment")
    woe.add_argument("--frequency-hz", type=float, default=42.0)
    woe.add_argument("--duration-seconds", type=float, default=6.0)
    woe.add_argument("--seed", type=int, default=7)
    args = parser.parse_args(argv)
    if args.command in {"demo", "run-scenario"}:
        return run_demo(args.scenario if args.command == "demo" else args.path)
    if args.command == "eoi-demo":
        return run_eoi_demo(args.scenario, args.trials)
    if args.command == "woe-demo":
        return run_woe_demo(
            frequency_hz=args.frequency_hz,
            duration_seconds=args.duration_seconds,
            seed=args.seed,
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
