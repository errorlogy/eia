"""Tick 147: routing (beta 0 / 2) x homotopic boost (h 0 / 0.1) on the connectome drive-unit model. E_norm of hemispheres,
SC communities and EIA map (true time-averaged W). 2 subjects x 1 seed."""
import numpy as np, scipy.sparse as sps
import brain_eia as b
from tick14_boundaries import louvain, HEMI, MODLAB
from tick38_homotopic import H
from tick146_routing_brain import sim, E_norm, unit_matrix, reg, R

eia = np.where(MODLAB >= 0, MODLAB, 100 + np.arange(R))
print(f"{'beta':>5}{'h':>5}{'hemispheres':>13}{'SC communities':>16}{'EIA map':>9}")
for h in (0.0, 0.1):
    for beta in (0.0, 2.0):
        rows = []
        for s_ in b.SUBJECTS[:2]:
            C, _ = b.load(s_); sc = louvain(C, 1.0, 146)
            W1 = sps.csr_matrix(unit_matrix(C + h * H, 1)); lo, hi = 0.3, 8.0
            for _ in range(10):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(W1*mid, 1, beta, 1500)[0].mean() < 0.03 else (lo, mid)
            sp, Wm = sim(W1*(lo+hi)/2, 1, beta, 4000); rng = np.random.default_rng(1)
            rows.append([E_norm(sp, Wm, lab[reg], rng) for lab in (HEMI, sc, eia)])
        m = np.mean(rows, 0); print(f"{beta:>5}{h:>5}{m[0]:>13.2f}{m[1]:>16.2f}{m[2]:>9.2f}", flush=True)
