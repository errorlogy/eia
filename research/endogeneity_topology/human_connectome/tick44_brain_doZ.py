"""Tick 44: do(Z) in the human model — does gating give containment (toy A4) in a brain?
Target = LOO-consensus block holding most DMN regions. do(Z): raise its bifurcation parameter a from
-0.02 to +0.02 for 30 s at t0 = 400 s (exact twin, same noise). Measured over the next 120 s:
relative envelope change inside the target vs outside, and change of the EIA initiation drive
(SAL+BG+SMA envelope). Conditions: no gate, gate, gate + homotopic 0.05. 4 subjects x 2 seeds."""
import numpy as np
import brain_eia as b
from tick14_boundaries import louvain
from tick16_fit import G, w0
from tick20_crossval import labels_of, gate
from tick38_homotopic import H

def sim(Ce, seed, target=None, T=560.0, dt=0.1, t0=400.0, dur=30.0):
    rng = np.random.default_rng(seed); n = 94; om = 2*np.pi*w0; deg = Ce.sum(1); sq = np.sqrt(dt)*0.02
    z = 0.1*(rng.standard_normal(n)+1j*rng.standard_normal(n)); env = []
    a = np.full(n, -0.02)
    for t in range(int(T/dt)):
        av = a.copy()
        if target is not None and t0 <= t*dt < t0 + dur: av[target] = 0.02
        z = z + dt*((av+1j*om)*z - np.abs(z)**2*z + G*(Ce@z-deg*z)) + sq*(rng.standard_normal(n)+1j*rng.standard_normal(n))
        if t % 5 == 0: env.append(np.abs(z))
    return np.array(env)          # every 0.5 s

if __name__ == "__main__":
    res = {}
    for s in b.SUBJECTS:
        train = [x for x in b.SUBJECTS if x != s]
        co = sum((labels_of(x)[:, None] == labels_of(x)[None, :]).astype(float) for x in train) / 3
        np.fill_diagonal(co, 0); cons = louvain(co, 1.0, 21)
        tb = max(set(cons), key=lambda k: np.isin(np.flatnonzero(cons == k), b.IDX["DMN"]).sum())
        tgt = np.flatnonzero(cons == tb); out = np.setdiff1d(np.arange(94), tgt)
        loop = np.setdiff1d(b.INIT_LOOP, tgt)
        C, _ = b.load(s)
        for name, Ce in [("no gate", C), ("gate", gate(C, cons)), ("gate+homotopic", gate(C + 0.05*H, cons))]:
            for seed in (1, 2):
                tw = sim(Ce, seed); pe = sim(Ce, seed, tgt)
                w = slice(int(400/0.5), int(520/0.5)); base = slice(int(200/0.5), int(400/0.5))
                rin = pe[w][:, tgt].mean() / tw[w][:, tgt].mean() - 1
                rout = pe[w][:, out].mean() / tw[w][:, out].mean() - 1
                rloop = pe[w][:, loop].mean() / tw[w][:, loop].mean() - 1 if len(loop) else np.nan
                res.setdefault(name, []).append((len(tgt), rin, rout, rloop, rout / rin if rin else np.nan))
    print(f"{'condition':<16}{'|target|':>9}{'d inside':>10}{'d outside':>11}{'d init-loop':>12}{'leak ratio':>11}")
    for name, rows in res.items():
        m = np.nanmean(rows, 0); print(f"{name:<16}{m[0]:>9.0f}{m[1]:>10.2%}{m[2]:>11.2%}{m[3]:>12.2%}{m[4]:>11.3f}")
