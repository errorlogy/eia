"""Tick 60: tension sets the uncertainty *target*, not its growth rate.
  u <- u + aging_k * (u*(e) - u) + beta_u * inp * (1 - u) - resolve * u * s,   u*(e) = u0 + (1 - u0) * e
Aging now relaxes toward a tension-dependent level (u0 = 0.2), so the level of BeliefField tension survives.
Metrics: Spearman(tension, intensity), first-initiative agreement with the current pipeline (7 scenarios x 3 seeds),
and silent intrinsic dynamics (ISI CV of motive bursts over 3000 steps at fixed moderate tension)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

import tick30_pipeline as h
from population_drives import PopulationDriveEngine, PopulationParams

U0 = 0.2


class TargetEngine(PopulationDriveEngine):
    aging_k = 0.02

    def step(self, ext=None, boost=None):
        p, st = self.p, self.state
        if boost:
            for k, v in boost.items():
                st.u[self.label == list(boost).index(k)] = v
        inp = self.W @ st.s
        e = np.zeros(len(st.u)) if ext is None else np.asarray(ext)[self.label]
        target = U0 + (1 - U0) * np.clip(e, 0, 1)
        st.u = np.clip(st.u + self.aging_k * (target - st.u) + p.beta_u * inp * (1 - st.u) - p.resolve * st.u * st.s, 0, 1)
        st.d = np.clip((1 - p.rho) * st.d + p.alpha * st.u + inp + p.sigma * self.rng.standard_normal(len(st.d)) - 0.8 * st.s, 0, 1)
        st.s = ((st.d > p.theta) & (st.refr <= 0)).astype(float)
        st.refr = np.where(st.s > 0, p.refractory, st.refr - 1)
        per = np.array([st.s[self.label == k].mean() for k in range(3)])
        st.history.append(per); st.tick += 1
        return per


class TargetAdapter(h.PopDriveAdapter):
    def __init__(self) -> None:
        import copy
        self.engine = TargetEngine(copy.deepcopy(self.params))
        from eia.drives import DriveState
        self.state = DriveState()

    def compute(self, field, **kw):
        m = super().compute(field, **kw)
        if m.dominant_drive is None:   # pipeline.py:159 assumes a dominant drive (crashes on all-zero drives)
            m = m.model_copy(update={"dominant_drive": max(m.signals, key=lambda s_: s_.intensity).drive})
        return m


if __name__ == "__main__":
    ref = {}
    h.use_population(False)
    for sp in h.SCENARIOS:
        r = h.pl.run_scenario(sp, traces_dir=Path("_traces"), seed=100)
        ref[sp.stem] = (r["initiative"].candidate.kind.value, r["initiative"].candidate.target_belief_id)
    print(f"{'aging_k':>8}{'alpha':>7}{'corr':>7}{'1st same':>10}{'mean int.':>10}{'silent ISI CV':>15}")
    for ak in (0.01, 0.05):
        for alpha in (0.14, 0.20):
            ten, inten, same = [], [], []
            for sp in h.SCENARIOS:
                for seed in (1, 2, 3):
                    h.use_population(True); h.pl.DriveEngine = TargetAdapter
                    TargetEngine.aging_k = ak; TargetAdapter.params = PopulationParams(seed=seed, mu=0.05, alpha=alpha)
                    r = h.pl.run_scenario(sp, traces_dir=Path("_traces"), seed=100)
                    for s in r["motivation"].signals:
                        ten.append(s.error_term); inten.append(s.intensity)
                    same.append((r["initiative"].candidate.kind.value, r["initiative"].candidate.target_belief_id) == ref[sp.stem])
            h.use_population(False)
            eng = TargetEngine(PopulationParams(seed=7, mu=0.05, alpha=alpha)); ev = []
            for t in range(3000):
                per = eng.step(np.array([0.5, 0.5, 0.5]))
                if (per >= eng.p.burst_frac).any():
                    ev.append(t)
            isi = np.diff(ev); cv = isi.std() / isi.mean() if len(isi) > 2 else float("nan")
            print(f"{ak:>8}{alpha:>7}{spearmanr(ten, inten)[0]:>7.2f}{np.mean(same):>10.2f}{np.mean(inten):>10.2f}{cv:>9.2f} ({len(ev)} ev)", flush=True)
