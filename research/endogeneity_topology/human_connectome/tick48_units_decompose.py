"""Tick 48: B12 with all 4 subjects and a decomposition: which ingredient smooths the onset?
Variants: rewired, plain SC, homotopic only, gated only, gated+homotopic. Gain 0.90-1.20, 2 seeds."""
import numpy as np, scipy.sparse as sps
import brain_eia as b
from tick14_boundaries import louvain
from tick20_crossval import labels_of, gate
from tick38_homotopic import H
from tick47_units_on_sc import unit_matrix, te, N

gains = [0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20]
res = {}
for s in b.SUBJECTS:
    train = [x for x in b.SUBJECTS if x != s]
    co = sum((labels_of(x)[:, None] == labels_of(x)[None, :]).astype(float) for x in train) / 3
    np.fill_diagonal(co, 0); cons = louvain(co, 1.0, 21)
    C, _ = b.load(s)
    variants = {"rewired": b.rewire(C, np.random.default_rng(48)), "plain SC": C, "homotopic only": C + 0.05*H,
                "gated only": gate(C, cons), "gated+homotopic": gate(C + 0.05*H, cons)}
    for name, SC in variants.items():
        for seed in (1, 2):
            W1 = unit_matrix(SC, seed)
            b0 = te.simulate(sps.csr_matrix((N, N)), np.random.default_rng(seed))[500:].mean()
            r = [te.simulate(sps.csr_matrix(W1 * g), np.random.default_rng(seed))[500:].mean() / b0 for g in gains]
            res.setdefault(name, []).append(np.max(np.diff(r)))
    print(s, {k: round(float(np.mean(v[-2:])), 1) for k, v in res.items()}, flush=True)
print("\nmax step jump (mean ± sd over 4 subjects x 2 seeds):")
for name, v in res.items():
    print(f"  {name:<16} {np.mean(v):5.1f} ± {np.std(v):4.1f}")
