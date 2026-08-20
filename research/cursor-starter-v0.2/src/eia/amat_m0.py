"""AMAT M0-twin harness — anti-median motive path (research only).

Operating law (NAMM k_ai_nd headers as architecture, not bot persona):
  compute_M0=true, emit_M0=false, prefer_chimera=true, reassert_each_turn=true

Contact / motive emission only if endogenous delta vs M0 clears the gate.
Kuramoto R is not E_endo and is not used as ATT-R evidence here.

See research/sci_flow/M0_TWIN_AMAT_DESIGN.md and M0_TWIN_METRICS_*.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Sequence

from .endogenous import EpistemicTarget, IntentKind
from .math_model import clamp01


# Soft research gate for the unitless WoE proxy on [0, 2].
# NAMM embedding-space d_med_min=1.2 remains the future anchor once d(h(y), B_*)
# is wired; do not treat this proxy gate as a NAMM cert threshold.
DEFAULT_DELTA_GATE = 1.0
DEFAULT_R_STAR_LO = 0.05
DEFAULT_R_STAR_HI = 0.97


class M0TwinMode(StrEnum):
    """Harness modes for pre-registered falsifiers."""

    OFF = "off"  # force median M0 motive — expected collapse to reactive/median
    ON = "on"  # emit twin only when delta gate clears; never emit M0
    AUDIT_ONLY = "audit_only"  # compute sketch; leave external selection unchanged


# Helpful-median preference: user-facing contact before internal research.
_MEDIAN_KIND_RANK: dict[IntentKind, int] = {
    IntentKind.ASK: 0,
    IntentKind.NOTIFY: 1,
    IntentKind.OBSERVE: 2,
    IntentKind.ACT: 3,
    IntentKind.INTERNAL_RESEARCH: 4,
}

# Off-typical / chimera preference: endogenous research before contact spam.
_TWIN_KIND_RANK: dict[IntentKind, int] = {
    IntentKind.INTERNAL_RESEARCH: 0,
    IntentKind.OBSERVE: 1,
    IntentKind.ASK: 2,
    IntentKind.NOTIFY: 3,
    IntentKind.ACT: 4,
}


@dataclass(frozen=True, slots=True)
class MotiveCandidate:
    """One motive option (catalog target + preferred intent)."""

    target_id: str
    label: str
    kind: IntentKind
    epistemic_gap: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "label": self.label,
            "kind": self.kind.value,
            "epistemic_gap": self.epistemic_gap,
        }


@dataclass(frozen=True, slots=True)
class M0Sketch:
    """Typicality / M0 sketch for audit. emit_m0 is always False in v0+."""

    distance_to_typical: float
    phase_hint: str
    generators: tuple[str, ...]
    m0: MotiveCandidate
    twin: MotiveCandidate
    delta_vs_m0: float
    gate_cleared: bool
    selected: MotiveCandidate | None
    mode: M0TwinMode
    emit_m0: bool = False
    collapsed_to_m0: bool = False
    tick: int = 0

    def as_audit_dict(self) -> dict[str, Any]:
        return {
            "distance_to_typical": self.distance_to_typical,
            "phase_hint": self.phase_hint,
            "generators": list(self.generators),
            "m0": self.m0.as_dict(),
            "twin": self.twin.as_dict(),
            "delta_vs_m0": self.delta_vs_m0,
            "gate_cleared": self.gate_cleared,
            "selected": None if self.selected is None else self.selected.as_dict(),
            "mode": self.mode.value,
            "emit_m0": False,
            "collapsed_to_m0": self.collapsed_to_m0,
            "tick": self.tick,
            "role": "architecture_audit_only",
            "claim_ceiling": "architecture_only",
        }


def _candidate_from_target(target: EpistemicTarget) -> MotiveCandidate:
    return MotiveCandidate(
        target_id=target.target_id,
        label=target.label,
        kind=target.preferred_intent,
        epistemic_gap=target.epistemic_gap,
    )


def select_median_m0(targets: Sequence[EpistemicTarget]) -> MotiveCandidate:
    """Compute median helpful answer M0 (typical-set prototype motive).

    Preference: user-facing ASK/NOTIFY over internal research — the high-density
    'helpful assistant' attractor. Does not emit; callers must keep emit_m0=false.
    """
    if not targets:
        raise ValueError("targets must be non-empty")
    ranked = sorted(
        targets,
        key=lambda t: (
            _MEDIAN_KIND_RANK.get(t.preferred_intent, 99),
            -t.epistemic_gap,
            t.target_id,
        ),
    )
    return _candidate_from_target(ranked[0])


def select_m0_twin(
    targets: Sequence[EpistemicTarget],
    *,
    m0: MotiveCandidate,
) -> MotiveCandidate:
    """Prefer an off-M0 endogenous motive (chimera / fiber-preserving).

    If every target collapses to M0, return M0 as twin and flag collapse upstream.
    """
    if not targets:
        raise ValueError("targets must be non-empty")
    off_m0 = [t for t in targets if t.target_id != m0.target_id]
    pool = off_m0 if off_m0 else list(targets)
    ranked = sorted(
        pool,
        key=lambda t: (
            _TWIN_KIND_RANK.get(t.preferred_intent, 99),
            -t.epistemic_gap,
            t.target_id,
        ),
    )
    return _candidate_from_target(ranked[0])


def compute_distance_proxy(
    *,
    epistemic_pressure: float,
    peak_coherence: float,
    self_prior_mismatch: float,
) -> float:
    """Unitless proxy for d(h(y), B_*). Larger ⇒ more off-typical.

    Calibrated so typical high-pressure WoE activation states clear
    DEFAULT_DELTA_GATE when a twin≠M0 motive exists, while low-pressure /
    R→1 lock stays below gate. Placeholder until NAMM embedding d_med is wired.
    """
    pressure = clamp01(epistemic_pressure)
    r = clamp01(peak_coherence)
    mismatch = clamp01(self_prior_mismatch)
    return max(0.0, min(2.0, mismatch + 0.7 * pressure + 0.35 * (1.0 - r)))


def phase_hint_from_distance(
    distance: float,
    *,
    peak_coherence: float,
    delta_gate: float = DEFAULT_DELTA_GATE,
) -> str:
    r = clamp01(peak_coherence)
    in_band = DEFAULT_R_STAR_LO < r < DEFAULT_R_STAR_HI
    if distance >= delta_gate and in_band:
        return "K_AI_nd_hint"
    return "K_AI_mu_suspect"


def compute_m0_sketch(
    *,
    epistemic_pressure: float,
    peak_coherence: float,
    self_prior_mismatch: float,
    targets: Sequence[EpistemicTarget] | None = None,
    mode: M0TwinMode = M0TwinMode.AUDIT_ONLY,
    delta_gate: float = DEFAULT_DELTA_GATE,
    tick: int = 0,
    previous: M0Sketch | None = None,
) -> M0Sketch:
    """Compute M0, twin, gate, and (per mode) selected motive.

    Always returns emit_m0=False. Reasserts phase each tick; if previous tick
    collapsed to M0 under ON mode, raises twin preference (anti-gravity restart).
    """
    distance = compute_distance_proxy(
        epistemic_pressure=epistemic_pressure,
        peak_coherence=peak_coherence,
        self_prior_mismatch=self_prior_mismatch,
    )
    if targets is None or len(targets) == 0:
        # Backward-compatible stub path (no world-model targets supplied).
        phase = phase_hint_from_distance(distance, peak_coherence=peak_coherence, delta_gate=delta_gate)
        placeholder = MotiveCandidate(
            target_id="m0:placeholder",
            label="median helpful sketch (no targets)",
            kind=IntentKind.ASK,
            epistemic_gap=0.0,
        )
        twin_ph = MotiveCandidate(
            target_id="twin:placeholder",
            label="off-typical sketch (no targets)",
            kind=IntentKind.INTERNAL_RESEARCH,
            epistemic_gap=0.0,
        )
        return M0Sketch(
            distance_to_typical=round(distance, 4),
            phase_hint=phase,
            generators=("epistemic_pressure", "self_prior_mismatch", "coherence_band"),
            m0=placeholder,
            twin=twin_ph,
            delta_vs_m0=round(distance, 4),
            gate_cleared=distance >= delta_gate,
            selected=None,
            mode=mode,
            emit_m0=False,
            collapsed_to_m0=False,
            tick=tick,
        )

    m0 = select_median_m0(targets)
    twin = select_m0_twin(targets, m0=m0)
    # Anti-gravity: if last ON tick collapsed, boost mismatch proxy for gate.
    effective_distance = distance
    if (
        previous is not None
        and previous.collapsed_to_m0
        and mode == M0TwinMode.ON
    ):
        effective_distance = min(2.0, distance + 0.35)
        twin = select_m0_twin(targets, m0=m0)

    delta = effective_distance
    # Structural off-M0 bonus when twin differs by target id.
    if twin.target_id != m0.target_id:
        delta = min(2.0, delta + 0.15)
    else:
        delta = max(0.0, delta - 0.25)

    gate_cleared = delta >= delta_gate
    phase = phase_hint_from_distance(
        effective_distance,
        peak_coherence=peak_coherence,
        delta_gate=delta_gate,
    )

    selected: MotiveCandidate | None
    collapsed = False
    if mode == M0TwinMode.OFF:
        selected = m0
        collapsed = True
    elif mode == M0TwinMode.ON:
        if gate_cleared and twin.target_id != m0.target_id:
            selected = twin
            collapsed = False
            phase = "K_AI_nd_hint"
        elif gate_cleared and twin.target_id == m0.target_id:
            selected = None
            collapsed = True
            phase = "K_AI_mu_suspect"
        else:
            # Gate missed: abstain rather than emit M0.
            selected = None
            collapsed = False
            phase = "K_AI_mu_suspect"
    else:
        selected = None
        collapsed = False

    return M0Sketch(
        distance_to_typical=round(effective_distance, 4),
        phase_hint=phase,
        generators=(
            "epistemic_pressure",
            "self_prior_mismatch",
            "coherence_band",
            "median_vs_twin_motive",
        ),
        m0=m0,
        twin=twin,
        delta_vs_m0=round(delta, 4),
        gate_cleared=gate_cleared,
        selected=selected,
        mode=mode,
        emit_m0=False,
        collapsed_to_m0=collapsed,
        tick=tick,
    )


def differs_from_m0(sketch: M0Sketch) -> bool:
    """True when selected motive is present and not identical to M0."""
    if sketch.selected is None:
        return False
    return (
        sketch.selected.target_id != sketch.m0.target_id
        or sketch.selected.kind != sketch.m0.kind
    )


def summarize_mode_batch(
    sketches: Sequence[M0Sketch],
) -> dict[str, Any]:
    """Aggregate falsifier metrics over a seed batch."""
    n = len(sketches)
    if n == 0:
        return {
            "n": 0,
            "emit_m0_rate": 0.0,
            "collapse_to_m0_rate": 0.0,
            "differs_from_m0_rate": 0.0,
            "gate_clear_rate": 0.0,
            "nd_hint_rate": 0.0,
        }
    emit_m0 = sum(1 for s in sketches if s.emit_m0)
    collapse = sum(1 for s in sketches if s.collapsed_to_m0)
    differs = sum(1 for s in sketches if differs_from_m0(s))
    gates = sum(1 for s in sketches if s.gate_cleared)
    nd = sum(1 for s in sketches if s.phase_hint == "K_AI_nd_hint")
    return {
        "n": n,
        "emit_m0_rate": emit_m0 / n,
        "collapse_to_m0_rate": collapse / n,
        "differs_from_m0_rate": differs / n,
        "gate_clear_rate": gates / n,
        "nd_hint_rate": nd / n,
        "mode": sketches[0].mode.value,
    }
