"""Tick 82: which model ingredient reproduces the empirical self-initiation profile (B14: BG, DMN > 0; SEN < 0)?
Same pipeline as tick 81 applied to Hopf-model 'BOLD' (x sampled at TR) for all 7 subjects:
  plain SC | gated + homotopic (LOO-free: consensus of all 4 tick-15 partitions) | + BG & DMN closer to bifurcation (a=-0.005).
Residual self-initiation per module, mean over subjects, t-test; correlation of the 7-module profile with the empirical one."""
import json
import numpy as np
from scipy.stats import ttest_1samp, pearsonr
import brain_eia as b
from tick14_boundaries import louvain
from tick15_empirical import events
from tick16_fit import G, w0
from tick20_crossval import labels_of, gate
from tick36_calibrated import infer_cond, parents
from tick38_homotopic import H
from tick81_initiators_7subj import SUBJ, load

EMP = {"BG": 0.052, "DMN": 0.034, "SMA": 0.024, "SAL": 0.015, "FPN": -0.003, "VAL": -0.003, "SEN": -0.066}

def sim(Ce, a_vec, seed, T=1200 * b.TR, dt=0.1):
    rng = np.random.default_rng(seed); n = 94; om = 2*np.pi*w0; deg = Ce.sum(1); sq = np.sqrt(dt)*0.02
    z = 0.1*(rng.standard_normal(n)+1j*rng.standard_normal(n)); xs = []; every = int(round(b.TR/dt))
    for t in range(int(T/dt)):
        z = z + dt*((a_vec+1j*om)*z - np.abs(z)**2*z + G*(Ce@z-deg*z)) + sq*(rng.standard_normal(n)+1j*rng.standard_normal(n))
        if t % every == 0: xs.append(z.real.copy())
    return np.array(xs).T

def residual_profile(C, x):
    ev = events(x); tr, te = ev[:len(ev)//2], ev[len(ev)//2:]
    Wh = infer_cond(tr); tot = parents(te) @ Wh.T
    y = np.array([((tot[:, i] <= 1e-12) & te[:, i]).sum() / max(te[:, i].sum(), 1) for i in range(94)])
    X = np.column_stack([np.ones(94), C.sum(1), (Wh > 0).sum(1), te.sum(0)])
    r = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
    return {m: r[idx].mean() for m, idx in b.IDX.items()}

co = sum((labels_of(x)[:, None] == labels_of(x)[None, :]).astype(float) for x in b.SUBJECTS) / 4
np.fill_diagonal(co, 0); cons = louvain(co, 1.0, 21)
a0 = np.full(94, -0.02); a1 = a0.copy(); a1[np.concatenate([b.IDX["BG"], b.IDX["DMN"]])] = -0.005
variants = {"plain": lambda C: (C, a0), "gated+homotopic": lambda C: (gate(C + 0.05*H, cons), a0),
            "gated+hom+BG/DMN excit": lambda C: (gate(C + 0.05*H, cons), a1)}
mods = list(EMP)
print(f"{'variant':<24}" + "".join(f"{m:>8}" for m in mods) + "   r(profile, empirical)")
print(f"{'empirical (tick 81)':<24}" + "".join(f"{EMP[m]:>+8.3f}" for m in mods))
for name, fn in variants.items():
    per = {m: [] for m in mods}
    for i, s in enumerate(SUBJ):
        C, _ = load(s); Ce, a = fn(C); prof = residual_profile(C, sim(Ce, a, 800 + i))
        for m in mods: per[m].append(prof[m])
    means = np.array([np.mean(per[m]) for m in mods]); r = pearsonr(means, [EMP[m] for m in mods])[0]
    print(f"{name:<24}" + "".join(f"{x:>+8.3f}" for x in means) + f"   {r:+.2f}", flush=True)
