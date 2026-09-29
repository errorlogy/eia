"""Tick 84: can weaker cortical input to the basal ganglia explain their empirical self-initiation excess (B14: +0.052)?
Plain Hopf model; incoming SC of BG regions scaled by k in {1, 0.3, 0.1} (rows of C). All 7 subjects, 2 seeds.
Module residual self-initiation (tick 81 pipeline), BG vs empirical; full-profile r with the empirical profile."""
import numpy as np
from scipy.stats import pearsonr
import brain_eia as b
from tick81_initiators_7subj import SUBJ, load
from tick82_model_initiators import sim, residual_profile, EMP

mods = list(EMP); a0 = np.full(94, -0.02)
print(f"{'k (BG input)':<13}" + "".join(f"{m:>8}" for m in mods) + "   r vs empirical")
for k in (1.0, 0.3, 0.1):
    per = {m: [] for m in mods}
    for i, s in enumerate(SUBJ):
        C, _ = load(s); Ck = C.copy(); Ck[b.IDX["BG"], :] *= k
        for seed in (1, 2):
            prof = residual_profile(C, sim(Ck, a0, 1000 + 10 * i + seed))
            for m in mods: per[m].append(prof[m])
    means = np.array([np.mean(per[m]) for m in mods])
    print(f"{k:<13}" + "".join(f"{x:>+8.3f}" for x in means) + f"   {pearsonr(means, [EMP[m] for m in mods])[0]:+.2f}", flush=True)
print(f"{'empirical':<13}" + "".join(f"{EMP[m]:>+8.3f}" for m in mods))
