"""Tick 41: metastable motive decomposition in a PopulationDriveEngine-style engine.
Units keep their drive identity (readout), but the *coupling* is gated by a decomposition:
  D0 = drive-aligned groups (epistemic / coherence / commitment)
  D1, D2 = cross-drive coalitions (each group holds 1/3 of every drive's units)
W_k = A * (g_in within group, g_out between), A = unstructured random graph (degree 5).
Conditions: fixed D0 | metastable D0<->D1<->D2 (mean dwell 300 ticks) | fixed D1 (coalitions only) | ungated.
Rate-matched: gain bisected per mode/seed to mean unit activity 0.03.
Metrics (10 seeds): boost of a non-dominant drive -> Δ self / Δ rest; co-initiative repertoire entropy
(which subsets of drives burst together); initiative rate."""

from __future__ import annotations

import numpy as np

from population_drives import DRIVES, PopulationDriveEngine, PopulationParams

U, NDR = 60, 3
N = U * NDR


def decompositions(rng):
    drive = np.repeat(np.arange(NDR), U)
    ds = [drive]
    for _ in range(2):
        lab = np.empty(N, int)
        for d in range(NDR):
            idx = rng.permutation(np.flatnonzero(drive == d))
            for g in range(NDR):
                lab[idx[g * U // NDR:(g + 1) * U // NDR]] = g
        ds.append(lab)
    return ds


class MetaEngine(PopulationDriveEngine):
    def __init__(self, params, mode, dwell=300.0, g_in=3.0, g_out=0.03):
        super().__init__(params)
        rng = np.random.default_rng(params.seed + 5)
        A = np.triu(rng.random((N, N)) < 5.0 / (N - 1), 1).astype(float); A = A + A.T
        self.decs = decompositions(rng)
        Ws = []
        for lab in self.decs:
            Wk = A * np.where(lab[:, None] == lab[None, :], g_in, g_out)
            Ws.append(Wk * (params.gain / max(np.max(np.abs(np.linalg.eigvals(Wk))), 1e-9)))
        A1 = A * (params.gain / max(np.max(np.abs(np.linalg.eigvals(A))), 1e-9))
        self.mode, self.dwell, self.Ws, self.A1 = mode, dwell, Ws, A1
        self.k = 0; self.sw_rng = np.random.default_rng(params.seed + 9)
        self.W = self._current()

    def _current(self):
        return {"fixed_D0": self.Ws[0], "fixed_D1": self.Ws[1], "ungated": self.A1}.get(self.mode, self.Ws[self.k])

    def step(self, ext=None, boost=None):
        if self.mode == "metastable" and self.sw_rng.random() < 1.0 / self.dwell:
            self.k = (self.k + self.sw_rng.integers(1, 3)) % 3
            self.W = self.Ws[self.k]
        return super().step(ext, boost)


GAIN = {}


def calibrate(mode, seed, target=0.03):
    """Bisect coupling gain so mean unit activity (ticks 500-1500) ~= target (rate matching)."""
    lo, hi = 0.3, 3.0
    for _ in range(9):
        mid = (lo + hi) / 2
        eng = MetaEngine(PopulationParams(seed=seed, units=U, gain=mid), mode)
        act = np.mean([eng.step().mean() for _ in range(1500)][500:])
        lo, hi = (mid, hi) if act < target else (lo, mid)
    GAIN[(mode, seed)] = (lo + hi) / 2


def run(mode, seed, t0=1500, horizon=400, boost=None):
    eng = MetaEngine(PopulationParams(seed=seed, units=U, gain=GAIN.get((mode, seed), 1.0)), mode)
    eng.rng = np.random.default_rng(seed + 999)
    hist = [eng.step(boost={boost: 1.0} if (boost is not None and t == t0) else None) for t in range(t0 + horizon)]
    return np.array(hist)


def entropy_of_patterns(h, thr):
    pats = [tuple(row >= thr) for row in h[500:] if (row >= thr).any()]
    if not pats: return 0.0, 0.0
    _, c = np.unique(np.array(pats), axis=0, return_counts=True); p = c / c.sum()
    return float(-(p * np.log2(p)).sum()), len(pats) / len(h[500:])


if __name__ == "__main__":
    thr = PopulationParams().burst_frac
    z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
    print(f"{'mode':<11}{'gain':>6}{'init rate':>10}{'pattern H':>10}{'Δself':>8}{'z':>6}{'Δrest':>8}{'z':>6}")
    for mode in ["fixed_D0", "metastable", "fixed_D1", "ungated"]:
        eff, Hs, rates = [], [], []
        for seed in range(1, 11):
            calibrate(mode, seed)
            base = run(mode, seed)
            H, rate = entropy_of_patterns(base, thr); Hs.append(H); rates.append(rate)
            dom = int(np.argmax(base[1450:1500].sum(0)))
            for k in DRIVES:
                i = DRIVES.index(k)
                if i == dom: continue
                pert = run(mode, seed, boost=k)
                eff.append(((pert[1500:, i] - base[1500:, i]).sum() * U,
                            (np.delete(pert[1500:], i, 1) - np.delete(base[1500:], i, 1)).sum() * U))
        e = np.array(eff)
        print(f"{mode:<11}{np.mean([GAIN[(mode, s_)] for s_ in range(1, 11)]):>6.2f}{np.mean(rates):>10.3f}{np.mean(Hs):>10.2f}{e[:,0].mean():>8.1f}{z(e[:,0]):>6.2f}{e[:,1].mean():>8.1f}{z(e[:,1]):>6.2f}", flush=True)
