"""Tick 37: does gating convert anatomical -> functional self-boundaries? Calibrated E_norm (tick 36).
Per held-out subject: model with no gate, LOO-consensus gate (3, 0.03), shuffled-consensus gate.
Scored partitions: subject's own empirical parts (tick 15), EIA map, hemispheres, SC communities."""
import json, zlib
import numpy as np
import brain_eia as b
from tick14_boundaries import louvain, MODLAB, HEMI
from tick15_empirical import events
from tick20_crossval import labels_of, sim, gate
from tick36_calibrated import infer_cond, E_norm

eia = MODLAB.copy(); eia[MODLAB < 0] = 100 + np.arange((MODLAB < 0).sum())
conds = ["no gate", "consensus gate", "shuffled gate"]
agg = {c: [] for c in conds}
print(f"{'held-out':<9}{'condition':<16}{'own parts':>10}{'EIA map':>9}{'hemi':>7}{'SC comm':>9}")
for held in b.SUBJECTS:
    train = [s for s in b.SUBJECTS if s != held]
    co = sum((labels_of(s)[:, None] == labels_of(s)[None, :]).astype(float) for s in train) / 3
    np.fill_diagonal(co, 0); cons = louvain(co, 1.0, 21)
    C, _ = b.load(held); own = labels_of(held); sc = louvain(C, 1.0, 37)
    shuf = cons[np.random.default_rng(37).permutation(94)]
    for name, Ce in [("no gate", C), ("consensus gate", gate(C, cons)), ("shuffled gate", gate(C, shuf))]:
        rows = []
        for seed in (61, 62):
            ev = events(sim(Ce, seed)); tr, te = ev[:len(ev)//2], ev[len(ev)//2:]
            Wh = infer_cond(tr); rng = np.random.default_rng(seed)
            rows.append([E_norm(te, Wh, lab, rng) for lab in (own, eia, HEMI, sc)])
        m = np.mean(rows, 0); agg[name].append(m)
        print(f"{held:<9}{name:<16}" + "".join(f"{v:>{w_}.2f}" for v, w_ in zip(m, (10, 9, 7, 9))), flush=True)
print("\nmeans (empirical reference, tick 36: own 0.68, EIA 0.25, hemi 0.05, SC 0.24)")
for c in conds:
    m = np.mean(agg[c], 0); print(f"  {c:<16}" + "".join(f"{v:>{w_}.2f}" for v, w_ in zip(m, (8, 9, 7, 9))))
