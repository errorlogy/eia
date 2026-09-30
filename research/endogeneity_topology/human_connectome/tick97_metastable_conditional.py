"""Tick 97: B10 re-checked with the conditional detector (tick 96 metrics). Models (homotopic h=0.05): no gate, fixed
consensus gate, switching gate among the other 3 subjects' partitions (dwell 120 s). 4 subjects x 2 seeds.
Target (empirical, tick 96): split-half ARI 0.04, E_norm of first-half parts on second half 0.38."""
import numpy as np
import brain_eia as b
from tick14_boundaries import ari, louvain
from tick15_empirical import events
from tick20_crossval import labels_of, gate
from tick36_calibrated import infer_cond, E_norm
from tick38_homotopic import H
from tick40_metastable import sim_switch
from tick96_degeneracy_conditional import detect_cond

print(f"{'condition':<14}{'split-half ARI':>15}{'E_norm(l1 on h2)':>18}")
agg = {}
for s in b.SUBJECTS:
    C, _ = b.load(s); Ch = C + 0.05 * H
    reps = [labels_of(x) for x in b.SUBJECTS if x != s]
    co = sum((l[:, None] == l[None, :]).astype(float) for l in reps) / 3; np.fill_diagonal(co, 0); cons = louvain(co, 1.0, 21)
    for name, (Cs, dwell) in {"no gate": ([Ch], 0), "fixed gate": ([gate(Ch, cons)], 0),
                              "switch 120 s": ([gate(Ch, l) for l in reps], 120.0)}.items():
        for seed in (91, 92):
            x, _ = sim_switch(Cs, dwell, seed); ev = events(x); h1, h2 = ev[:len(ev)//2], ev[len(ev)//2:]
            l1, l2 = detect_cond(h1, seed), detect_cond(h2, seed + 1)
            agg.setdefault(name, []).append((ari(l1, l2), E_norm(h2, infer_cond(h1), l1, np.random.default_rng(seed))))
for name, rows in agg.items():
    m = np.mean(rows, 0); print(f"{name:<14}{m[0]:>15.2f}{m[1]:>18.2f}", flush=True)
print(f"{'empirical':<14}{0.04:>15.2f}{0.38:>18.2f}")
