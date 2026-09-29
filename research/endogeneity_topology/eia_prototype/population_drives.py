"""PopulationDriveEngine — research prototype that folds ticks 1–28 into an EIA-compatible drive engine.

Each DriveKind is a population of units (a motive = a module). Differences from eia.drives.DriveEngine:
  * internal generators: uncertainty aging + noise (drives evolve in silence, no pinning)
  * within-motive excitatory coupling, cross-motive coupling with mixing mu
    (excitatory or lateral-inhibitory — ticks 23–28)
  * BeliefField gradients are *inputs* that raise the motive's uncertainty, not the whole drive
Output is the same `Motivation` schema, so it can be swapped into the pipeline for experiments.
Not wired into src/ — exploratory only.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from datetime import datetime, timezone

import numpy as np

from eia.beliefs import BeliefField
from eia.schemas.motivation import DriveKind, Motivation, MotivationSignal

DRIVES = list(DriveKind)


@dataclass
class PopulationParams:
    units: int = 60
    degree: float = 5.0
    mu: float = 0.05                 # fraction of a unit's links that go to other motives
    cross_inhibitory: bool = False   # lateral inhibition between motives
    gain: float = 1.0                # spectral-radius-normalised coupling gain
    rho: float = 0.12
    alpha: float = 0.10
    theta: float = 0.60
    aging: float = 0.004
    resolve: float = 0.6
    beta_u: float = 0.15
    sigma: float = 0.03
    ext_gain: float = 0.05           # BeliefField gradient -> uncertainty drive
    refractory: int = 5
    window: int = 20                 # ticks for intensity readout
    burst_frac: float = 0.15         # fraction of a motive active in one tick = initiative event
    seed: int = 0


@dataclass
class PopulationState:
    d: np.ndarray
    u: np.ndarray
    s: np.ndarray
    refr: np.ndarray
    history: list = dc_field(default_factory=list)
    tick: int = 0


class PopulationDriveEngine:
    def __init__(self, params: PopulationParams | None = None) -> None:
        self.p = p = params or PopulationParams()
        self.rng = np.random.default_rng(p.seed)
        n = p.units * len(DRIVES)
        self.label = np.repeat(np.arange(len(DRIVES)), p.units)
        same = self.label[:, None] == self.label[None, :]
        p_in = p.degree * (1 - p.mu) / (p.units - 1)
        p_out = p.degree * p.mu / (n - p.units)
        A = np.triu(self.rng.random((n, n)) < np.where(same, p_in, p_out), 1).astype(float)
        A = A + A.T
        exc = np.where(same, A, 0.0 if p.cross_inhibitory else A)
        lam = max(np.max(np.abs(np.linalg.eigvals(exc))), 1e-9)
        W = A.copy()
        if p.cross_inhibitory:
            W[~same] *= -1
        self.W = W * (p.gain / lam)
        self.state = PopulationState(
            d=self.rng.uniform(0, 0.3, n), u=self.rng.uniform(0.2, 0.6, n),
            s=np.zeros(n), refr=np.zeros(n),
        )

    # -- dynamics -------------------------------------------------------------
    def step(self, ext: np.ndarray | None = None, boost: dict[DriveKind, float] | None = None) -> np.ndarray:
        p, st = self.p, self.state
        if boost:
            for k, v in boost.items():
                st.u[self.label == DRIVES.index(k)] = v
        inp = self.W @ st.s
        e = np.zeros_like(st.u) if ext is None else ext[self.label]
        st.u = np.clip(st.u + p.aging * (1 - st.u) + p.beta_u * inp * (1 - st.u) + p.ext_gain * e * (1 - st.u)
                       - p.resolve * st.u * st.s, 0, 1)
        st.d = np.clip((1 - p.rho) * st.d + p.alpha * st.u + inp
                       + p.sigma * self.rng.standard_normal(len(st.d)) - 0.8 * st.s, 0, 1)
        st.s = ((st.d > p.theta) & (st.refr <= 0)).astype(float)
        st.refr = np.where(st.s > 0, p.refractory, st.refr - 1)
        per_motive = np.array([st.s[self.label == k].mean() for k in range(len(DRIVES))])
        st.history.append(per_motive)
        st.tick += 1
        return per_motive

    def initiatives(self, per_motive: np.ndarray) -> list[DriveKind]:
        return [DRIVES[k] for k in np.flatnonzero(per_motive >= self.p.burst_frac)]

    # -- EIA-compatible readout -------------------------------------------------
    def compute(self, field: BeliefField | None = None, *, motivation_id: str = "mot-pop") -> Motivation:
        grads = field.gradient_snapshot() if field is not None else {k.value: 0.0 for k in DRIVES}
        ext = np.array([grads[k.value] for k in DRIVES])
        self.step(ext)
        recent = np.array(self.state.history[-self.p.window:])
        intensity = np.clip(recent.mean(0) / max(self.p.burst_frac, 1e-9), 0, 1)
        targets = {
            DriveKind.EPISTEMIC: [b.id for b in field.highest_entropy_beliefs(2)] if field else [],
            DriveKind.COHERENCE: [c[0] for c in field.contradictions[:2]] if field else [],
            DriveKind.COMMITMENT: [b.id for b in field.beliefs.values() if b.kind.value == "commitment"] if field else [],
        }
        signals = [
            MotivationSignal(
                drive=k, intensity=float(intensity[i]), error_term=float(ext[i]), decay_rate=self.p.rho,
                target_belief_ids=targets[k],
                explanation=f"{k.value}: population activity {recent.mean(0)[i]:.3f} over {len(recent)} ticks "
                            f"(mu={self.p.mu}, cross_inh={self.p.cross_inhibitory})",
            )
            for i, k in enumerate(DRIVES)
        ]
        dom = max(signals, key=lambda s_: s_.intensity)
        return Motivation(
            id=motivation_id, timestamp=datetime.now(timezone.utc), signals=signals,
            composite_lex_score=(dom.intensity, float(ext[1]), float(ext[2])),
            dominant_drive=dom.drive if dom.intensity > 0 else None,
            parent_belief_update_ids=[u.id for u in field.updates[-3:]] if field else [],
        )
