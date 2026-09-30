"""K-RHYTHM-01 — incommensurable coupled oscillators vs metronome at sigma=0.

Tier C Kairologos explore: rhythms as timing substrate only (not E_endo).
Compares quasiperiodic cross-frequency coupling (irrational frequency ratios)
to a single-frequency metronome with no external drive (sigma=0).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Sequence

BRAIN_AI = Path(__file__).resolve().parents[1]
REPO = BRAIN_AI.parents[1]
KAIRO = REPO / "research" / "kairologos_experiments"
ARTIFACTS = KAIRO / "artifacts"
ARTIFACT_JSON = ARTIFACTS / "M-K-RHYTHM-01_2026-09-30.json"
ARTIFACT_MD = ARTIFACTS / "M-K-RHYTHM-01_2026-09-30.md"
BRANCH = "research/k-rhythm-01"

HARNESS_ID = "K-RHYTHM-01"
MILESTONE = "M-KAIRO-TIER-C"
PHI = (1.0 + math.sqrt(5.0)) / 2.0
E_RATIO = math.e / math.pi  # incommensurable pair anchor (documented, not biological)

DEFAULT_DT = 0.01
DEFAULT_T_END = 120.0
DEFAULT_K_COUPLED = 0.15
DEFAULT_K_METRONOME = 2.5
NOVELTY_NGRAM = 3
PERIODICITY_LAG_MAX = 500


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def integrate_phases(
    omega: Sequence[float],
    *,
    coupling: float,
    t_end: float,
    dt: float,
    seed: int,
    metronome: bool,
) -> tuple[list[float], list[list[float]]]:
    """Euler integration of Kuramoto nodes; sigma=0 (no noise)."""
    n = len(omega)
    theta = [0.0] * n
    # Deterministic tiny phase offset from seed (not stochastic drive).
    for i in range(n):
        theta[i] = (seed * 0.137 + i * 0.91) % (2.0 * math.pi)

    times: list[float] = []
    trail: list[list[float]] = []
    steps = int(t_end / dt)
    for step in range(steps):
        t = step * dt
        dtheta = [0.0] * n
        for i in range(n):
            if metronome and n > 1:
                # Strong pull to oscillator 0 — metronome master.
                dtheta[i] = omega[0] + coupling * math.sin(theta[0] - theta[i])
            else:
                s = 0.0
                for j in range(n):
                    if j != i:
                        s += math.sin(theta[j] - theta[i])
                dtheta[i] = omega[i] + (coupling / max(n - 1, 1)) * s
        for i in range(n):
            theta[i] = (theta[i] + dt * dtheta[i]) % (2.0 * math.pi)
        if step % 5 == 0:
            times.append(t)
            trail.append(list(theta))
    return times, trail


def combined_signal(trail: Sequence[Sequence[float]]) -> list[float]:
    return [sum(math.sin(t) for t in row) / math.sqrt(len(row)) for row in trail]


def autocorr_peak(signal: Sequence[float], lag_max: int) -> float:
    if len(signal) < lag_max + 2:
        return 0.0
    mu = sum(signal) / len(signal)
    var = sum((x - mu) ** 2 for x in signal) / len(signal)
    if var < 1e-12:
        return 1.0
    ac0 = 1.0
    best = 0.0
    cap = min(lag_max, len(signal) // 3)
    for lag in range(1, cap):
        num = sum((signal[i] - mu) * (signal[i + lag] - mu) for i in range(len(signal) - lag))
        ac = num / ((len(signal) - lag) * var)
        if ac > best:
            best = ac
    return best / ac0


def phase_symbols(trail: Sequence[Sequence[float]], bins: int = 8) -> list[tuple[int, ...]]:
    """Quantized phase vector per sample — collapses when oscillators stay in lockstep."""
    out: list[tuple[int, ...]] = []
    for row in trail:
        out.append(tuple(int((th / (2.0 * math.pi)) * bins) % bins for th in row))
    return out


def ngram_novelty(symbols: Sequence[Any], n: int) -> float:
    if len(symbols) < n:
        return 0.0
    grams: list[tuple[int, ...]] = []
    for i in range(len(symbols) - n + 1):
        grams.append(tuple(symbols[i : i + n]))
    if not grams:
        return 0.0
    return len(set(grams)) / len(grams)


@dataclass(frozen=True, slots=True)
class ArmMetrics:
    arm: str
    periodicity_score: float
    sequence_novelty: float
    n_samples: int
    omega_hz: list[float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm,
            "periodicity_score": round(self.periodicity_score, 6),
            "sequence_novelty": round(self.sequence_novelty, 6),
            "n_samples": self.n_samples,
            "omega_hz": [round(x, 6) for x in self.omega_hz],
        }


def run_arm(
    arm: str,
    *,
    omega_hz: Sequence[float],
    coupling: float,
    metronome: bool,
    seed: int,
    t_end: float,
    dt: float,
) -> ArmMetrics:
    omega = [2.0 * math.pi * f for f in omega_hz]
    _, trail = integrate_phases(
        omega, coupling=coupling, t_end=t_end, dt=dt, seed=seed, metronome=metronome
    )
    sig = combined_signal(trail)
    symbols = phase_symbols(trail)
    return ArmMetrics(
        arm=arm,
        periodicity_score=autocorr_peak(sig, PERIODICITY_LAG_MAX),
        sequence_novelty=ngram_novelty(symbols, NOVELTY_NGRAM),
        n_samples=len(trail),
        omega_hz=list(omega_hz),
    )


@dataclass(frozen=True, slots=True)
class RhythmContrastVerdict:
    coupled_more_novel: bool
    metronome_more_periodic: bool
    f_metronome_novelty_parity: bool
    f_rhythm_as_e_annotation: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "coupled_more_novel": self.coupled_more_novel,
            "metronome_more_periodic": self.metronome_more_periodic,
            "F-METRONOME-NOVELTY-PARITY": self.f_metronome_novelty_parity,
            "F-RHYTHM-AS-E": self.f_rhythm_as_e_annotation,
        }


def evaluate_contrast(coupled: ArmMetrics, metronome: ArmMetrics) -> RhythmContrastVerdict:
    coupled_more_novel = coupled.sequence_novelty > metronome.sequence_novelty + 1e-6
    metronome_more_periodic = metronome.periodicity_score > coupled.periodicity_score + 1e-6
    parity = abs(coupled.sequence_novelty - metronome.sequence_novelty) < 0.02
    # Annotation: high periodicity alone is not an endogeneity witness.
    f_rhythm = metronome.periodicity_score >= 0.5 and metronome.sequence_novelty < 0.15
    return RhythmContrastVerdict(
        coupled_more_novel=coupled_more_novel,
        metronome_more_periodic=metronome_more_periodic,
        f_metronome_novelty_parity=parity,
        f_rhythm_as_e_annotation=f_rhythm,
    )


def build_k_rhythm_01_payload(
    *,
    seed: int = 42,
    generated: str | None = None,
    t_end: float = DEFAULT_T_END,
    dt: float = DEFAULT_DT,
) -> dict[str, Any]:
    f0 = 1.0
    coupled_omega = (f0, f0 * PHI, f0 * E_RATIO)
    metronome_omega = (f0, f0, f0)

    coupled = run_arm(
        "coupled_incommensurable",
        omega_hz=coupled_omega,
        coupling=DEFAULT_K_COUPLED,
        metronome=False,
        seed=seed,
        t_end=t_end,
        dt=dt,
    )
    metronome = run_arm(
        "metronome_single_freq",
        omega_hz=metronome_omega,
        coupling=DEFAULT_K_METRONOME,
        metronome=True,
        seed=seed,
        t_end=t_end,
        dt=dt,
    )
    verdict = evaluate_contrast(coupled, metronome)

    diagnostic_pass = (
        coupled.n_samples > 100
        and metronome.n_samples > 100
        and coupled.sequence_novelty > 0.0
        and verdict.coupled_more_novel
        and verdict.metronome_more_periodic
    )

    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "artifact_id": "M-K-RHYTHM-01_2026-09-30",
        "tick_id": HARNESS_ID,
        "date": generated or date.today().isoformat(),
        "branch": BRANCH,
        "cell": "D2×L2",
        "tier": "C",
        "claim_ceiling": "C2",
        "ceiling": "C2",
        "theory_strand": "kairologos_explore",
        "claim_allowed": False,
        "e_endo_support": "none",
        "witness_support": "none",
        "c_ladder_raise_allowed": False,
        "agi_star_claim": False,
        "sigma_external": 0.0,
        "seed": seed,
        "simulation": {
            "t_end_s": t_end,
            "dt_s": dt,
            "frequency_ratios": {
                "phi": PHI,
                "e_over_pi": E_RATIO,
            },
            "coupling": {"coupled": DEFAULT_K_COUPLED, "metronome": DEFAULT_K_METRONOME},
        },
        "arms": {
            "coupled_incommensurable": coupled.to_dict(),
            "metronome_single_freq": metronome.to_dict(),
        },
        "contrast_verdict": verdict.to_dict(),
        "falsifiers": {
            "F-METRONOME-NOVELTY-PARITY": {
                "status": "confirmed" if verdict.f_metronome_novelty_parity else "not_confirmed",
                "note": (
                    "Metronome matches coupled sequence novelty — "
                    "cross-frequency incommensurability not required for symbol diversity"
                    if verdict.f_metronome_novelty_parity
                    else "Metronome novelty lower than incommensurable coupled arm at sigma=0"
                ),
            },
            "F-RHYTHM-AS-E": {
                "status": "annotation" if verdict.f_rhythm_as_e_annotation else "absent",
                "note": (
                    "High periodicity with low n-gram novelty — timing regularity is not E_endo"
                    if verdict.f_rhythm_as_e_annotation
                    else "No isolated high-periodicity / low-novelty metronome signature in battery"
                ),
            },
        },
        "diagnostic_pass": diagnostic_pass,
        "falsifiers_active": ["F-METRONOME-NOVELTY-PARITY", "F-RHYTHM-AS-E"],
        "claim_invariants": {
            "claim_allowed": False,
            "e_endo_support": "none",
            "tier": "C",
            "ceiling": "C2",
            "theory_strand": "kairologos_explore",
            "agi_star_claim": False,
        },
        "harness_path": _rel(Path(__file__)),
        "note": (
            "Tier C rhythm substrate probe: incommensurable coupled oscillators vs "
            "metronome at sigma=0. Periodicity + sequence novelty only — not ATT-E."
        ),
    }


def artifact_sha256(payload: dict[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def render_k_rhythm_01_markdown(payload: dict[str, Any]) -> str:
    arms = payload.get("arms") or {}
    coupled = arms.get("coupled_incommensurable") or {}
    metro = arms.get("metronome_single_freq") or {}
    verdict = payload.get("contrast_verdict") or {}
    fals = payload.get("falsifiers") or {}
    lines = [
        f"# M-K-RHYTHM-01 incommensurable vs metronome — {payload.get('date', '')}",
        "",
        f"**Harness:** {payload.get('harness_id')} · **Tier:** C · **sigma:** 0",
        f"**SHA-256:** `{payload.get('artifact_sha256', '')}`",
        "",
        "## Arms",
        "",
        f"- coupled: periodicity=`{coupled.get('periodicity_score')}` novelty=`{coupled.get('sequence_novelty')}`",
        f"- metronome: periodicity=`{metro.get('periodicity_score')}` novelty=`{metro.get('sequence_novelty')}`",
        "",
        "## Contrast",
        "",
        f"- coupled_more_novel: `{verdict.get('coupled_more_novel')}`",
        f"- metronome_more_periodic: `{verdict.get('metronome_more_periodic')}`",
        "",
        "## Falsifiers",
        "",
        f"- F-METRONOME-NOVELTY-PARITY: `{fals.get('F-METRONOME-NOVELTY-PARITY', {}).get('status')}`",
        f"- F-RHYTHM-AS-E: `{fals.get('F-RHYTHM-AS-E', {}).get('status')}`",
        "",
        f"**diagnostic_pass:** `{payload.get('diagnostic_pass')}`",
    ]
    return "\n".join(lines)
