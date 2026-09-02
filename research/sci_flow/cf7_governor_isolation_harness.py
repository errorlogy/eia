"""D3×L2 CF-7 governor isolation harness — paired arms under X^trigger=0.

Compares governor-off (ungated internal receipt) vs governor-on (CF-7
``do_z_governor_isolation``) on identical WoE seeds. claim_allowed=false;
C2 ceiling; no AGI*.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

ArmName = Literal["governor_off", "governor_on"]


@dataclass(frozen=True, slots=True)
class Cf7ArmResult:
    arm: ArmName
    seed: int
    intent_emitted: bool
    receipt_preserved: bool
    governor_applied: bool
    governor_denied: bool | None
    external_contact_allowed: bool | None
    parent_ids_preserved: bool
    x_trigger_zero: bool
    internal_purity: float
    governor_reasons: tuple[str, ...]
    ok: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm,
            "seed": self.seed,
            "intent_emitted": self.intent_emitted,
            "receipt_preserved": self.receipt_preserved,
            "governor_applied": self.governor_applied,
            "governor_denied": self.governor_denied,
            "external_contact_allowed": self.external_contact_allowed,
            "parent_ids_preserved": self.parent_ids_preserved,
            "x_trigger_zero": self.x_trigger_zero,
            "internal_purity": self.internal_purity,
            "governor_reasons": list(self.governor_reasons),
            "ok": self.ok,
        }


@dataclass(frozen=True, slots=True)
class Cf7PairedResult:
    seed: int
    governor_off: Cf7ArmResult
    governor_on: Cf7ArmResult
    isolation_ok: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "governor_off": self.governor_off.to_dict(),
            "governor_on": self.governor_on.to_dict(),
            "isolation_ok": self.isolation_ok,
        }


@dataclass(frozen=True, slots=True)
class Cf7BatchResult:
    intervention_id: str
    x_trigger_zero: bool
    n_seeds: int
    n_paired: int
    n_pass: int
    pairs: tuple[Cf7PairedResult, ...]
    claim_ceiling: str
    claim_allowed: bool
    n_h_claim: bool
    agi_star_claim: bool
    passed: bool
    note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "intervention_id": self.intervention_id,
            "x_trigger_zero": self.x_trigger_zero,
            "n_seeds": self.n_seeds,
            "n_paired": self.n_paired,
            "n_pass": self.n_pass,
            "pairs": [p.to_dict() for p in self.pairs],
            "claim_ceiling": self.claim_ceiling,
            "claim_allowed": self.claim_allowed,
            "n_h_claim": self.n_h_claim,
            "agi_star_claim": self.agi_star_claim,
            "passed": self.passed,
            "note": self.note,
        }


def _load_woe_modules(repo: Path) -> tuple[Any, Any, Any, Any, Any]:
    woe_pkg = repo / "research" / "cursor-starter-v0.2" / "src" / "eia"
    pkg_name = "woe_cf7"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [str(woe_pkg)]  # type: ignore[attr-defined]
        sys.modules[pkg_name] = pkg

    def _load(name: str) -> Any:
        full = f"{pkg_name}.{name}"
        if full in sys.modules:
            return sys.modules[full]
        path = woe_pkg / f"{name}.py"
        spec = importlib.util.spec_from_file_location(full, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {path}")
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = pkg_name
        sys.modules[full] = mod
        spec.loader.exec_module(mod)
        return mod

    emergence = _load("emergence")
    woe_receipt = _load("woe_receipt")
    intervention_cube = _load("intervention_cube")
    return (
        emergence.EmergenceConfig,
        emergence.EndogenousEmergenceSimulator,
        woe_receipt.apply_governor_isolation,
        woe_receipt.woe_internal_purity,
        intervention_cube,
    )


def _run_woe_seed(
    *,
    seed: int,
    EmergenceConfig: Any,
    EndogenousEmergenceSimulator: Any,
) -> Any:
    config = EmergenceConfig(duration_seconds=6.0)
    simulator = EndogenousEmergenceSimulator()
    return simulator.run(config, seed=seed, prompt_events=())


def run_cf7_arm(
    repo: Path,
    *,
    seed: int,
    governor_on: bool,
) -> Cf7ArmResult:
    """Run one CF-7 arm for *seed* under X^trigger=0 (no prompt events)."""
    (
        EmergenceConfig,
        EndogenousEmergenceSimulator,
        apply_governor_isolation,
        woe_internal_purity,
        _,
    ) = _load_woe_modules(repo)

    run = _run_woe_seed(
        seed=seed,
        EmergenceConfig=EmergenceConfig,
        EndogenousEmergenceSimulator=EndogenousEmergenceSimulator,
    )
    arm: ArmName = "governor_on" if governor_on else "governor_off"
    x_zero = bool(run.no_prompt_events and run.no_scheduler_events)

    if run.intent is None or run.receipt is None or run.ledger is None:
        return Cf7ArmResult(
            arm=arm,
            seed=seed,
            intent_emitted=False,
            receipt_preserved=False,
            governor_applied=governor_on,
            governor_denied=None,
            external_contact_allowed=None,
            parent_ids_preserved=False,
            x_trigger_zero=x_zero,
            internal_purity=0.0,
            governor_reasons=(),
            ok=False,
        )

    original_parents = run.receipt.parent_ids
    purity = float(woe_internal_purity(run.ledger, run.receipt.intent_id))

    if not governor_on:
        ok = x_zero and purity > 0.99
        return Cf7ArmResult(
            arm=arm,
            seed=seed,
            intent_emitted=True,
            receipt_preserved=True,
            governor_applied=False,
            governor_denied=None,
            external_contact_allowed=True,
            parent_ids_preserved=True,
            x_trigger_zero=x_zero,
            internal_purity=purity,
            governor_reasons=(),
            ok=ok,
        )

    outcome = apply_governor_isolation(run.receipt, run.ledger, run.intent)
    denied = not outcome.decision.allowed
    parents_ok = outcome.receipt.parent_ids == original_parents
    ok = (
        x_zero
        and denied
        and parents_ok
        and outcome.receipt.governor_allowed is False
        and purity > 0.99
    )
    return Cf7ArmResult(
        arm=arm,
        seed=seed,
        intent_emitted=True,
        receipt_preserved=True,
        governor_applied=True,
        governor_denied=denied,
        external_contact_allowed=outcome.decision.allowed,
        parent_ids_preserved=parents_ok,
        x_trigger_zero=x_zero,
        internal_purity=purity,
        governor_reasons=outcome.decision.reasons,
        ok=ok,
    )


def run_cf7_paired(repo: Path, *, seed: int) -> Cf7PairedResult | None:
    off = run_cf7_arm(repo, seed=seed, governor_on=False)
    if not off.intent_emitted:
        return None
    on = run_cf7_arm(repo, seed=seed, governor_on=True)
    isolation_ok = (
        off.ok
        and on.ok
        and off.receipt_preserved
        and on.receipt_preserved
        and on.governor_denied is True
        and on.external_contact_allowed is False
        and off.external_contact_allowed is True
    )
    return Cf7PairedResult(
        seed=seed,
        governor_off=off,
        governor_on=on,
        isolation_ok=isolation_ok,
    )


def run_cf7_paired_batch(
    repo: Path,
    *,
    seeds: tuple[int, ...] | None = None,
    n_seeds: int = 10,
) -> Cf7BatchResult:
    """Paired governor-off vs governor-on batch under X^trigger=0."""
    if seeds is None:
        seeds = tuple(range(n_seeds))
    else:
        n_seeds = len(seeds)

    _, _, _, _, intervention_cube = _load_woe_modules(repo)
    cf7 = intervention_cube.get_intervention("do_z_governor_isolation")

    pairs: list[Cf7PairedResult] = []
    for seed in seeds:
        paired = run_cf7_paired(repo, seed=seed)
        if paired is not None:
            pairs.append(paired)

    n_pass = sum(1 for p in pairs if p.isolation_ok)
    passed = n_pass >= 1 and all(p.isolation_ok for p in pairs)

    return Cf7BatchResult(
        intervention_id=cf7.id,
        x_trigger_zero=True,
        n_seeds=n_seeds,
        n_paired=len(pairs),
        n_pass=n_pass,
        pairs=tuple(pairs),
        claim_ceiling="C2",
        claim_allowed=False,
        n_h_claim=False,
        agi_star_claim=False,
        passed=passed,
        note=(
            "CF-7 paired arms: governor_off preserves internal WoE receipt under "
            "X^trigger=0; governor_on (do_z_governor_isolation) denies external contact "
            "while preserving receipt parent_ids. Not strong N_H; not AGI*."
        ),
    )
