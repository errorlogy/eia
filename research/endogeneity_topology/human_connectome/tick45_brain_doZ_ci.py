"""Tick 45: B11 with confidence — tick 44 design, 6 seeds x 4 subjects (n = 24 per condition),
no gate vs gate. z-scores of inside / outside / initiation-loop changes."""
import numpy as np
import brain_eia as b
from tick14_boundaries import louvain
from tick20_crossval import labels_of, gate
from tick44_brain_doZ import sim

res = {}
for s in b.SUBJECTS:
    train = [x for x in b.SUBJECTS if x != s]
    co = sum((labels_of(x)[:, None] == labels_of(x)[None, :]).astype(float) for x in train) / 3
    np.fill_diagonal(co, 0); cons = louvain(co, 1.0, 21)
    tb = max(set(cons), key=lambda k: np.isin(np.flatnonzero(cons == k), b.IDX["DMN"]).sum())
    tgt = np.flatnonzero(cons == tb); out = np.setdiff1d(np.arange(94), tgt); loop = np.setdiff1d(b.INIT_LOOP, tgt)
    C, _ = b.load(s)
    for name, Ce in [("no gate", C), ("gate", gate(C, cons))]:
        for seed in range(11, 17):
            tw = sim(Ce, seed); pe = sim(Ce, seed, tgt); w = slice(800, 1040)
            f = lambda idx: pe[w][:, idx].mean() / tw[w][:, idx].mean() - 1
            res.setdefault(name, []).append((f(tgt), f(out), f(loop)))
z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
print(f"{'condition':<10}{'inside':>10}{'z':>7}{'outside':>10}{'z':>7}{'loop':>9}{'z':>7}")
for name, rows in res.items():
    a = np.array(rows)
    print(f"{name:<10}" + "".join(f"{a[:,i].mean():>{w_}.2%}{z(a[:,i]):>7.2f}" for i, w_ in zip(range(3), (10, 10, 9))))
d = np.array(res["gate"]) - np.array(res["no gate"])
print(f"gate - no gate (paired): inside {d[:,0].mean():.2%} (z {z(d[:,0]):.2f}), outside {d[:,1].mean():.2%} (z {z(d[:,1]):.2f})")
