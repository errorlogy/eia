"""Tick 40: can metastable gating reproduce degenerate self-boundaries (tick 39: split-half ARI 0.09,
held-out E_norm ~0.45)? Repertoire = the other 3 subjects' empirical partitions (non-circular).
Conditions (all with homotopic h=0.05): no gate; fixed gate (LOO consensus); switching gate among the
3 repertoire partitions with mean dwell 30 s or 120 s. Metrics on model output, same pipeline as tick 39."""
import numpy as np
import brain_eia as b
from tick14_boundaries import ari, louvain
from tick15_empirical import events, detect
from tick16_fit import G, w0
from tick20_crossval import labels_of, gate
from tick36_calibrated import infer_cond, E_norm
from tick38_homotopic import H

def sim_switch(Cs, dwell, seed, T=1200 * b.TR, dt=0.1):
    rng = np.random.default_rng(seed); n = 94; om = 2*np.pi*w0; sq = np.sqrt(dt)*0.02
    z = 0.1*(rng.standard_normal(n)+1j*rng.standard_normal(n)); xs = []; every = int(round(b.TR/dt))
    k = rng.integers(len(Cs)); degs = [C.sum(1) for C in Cs]; switches = 0
    for t in range(int(T/dt)):
        if dwell and rng.random() < dt/dwell:
            k = (k + rng.integers(1, len(Cs))) % len(Cs); switches += 1
        z = z + dt*((-0.02+1j*om)*z - np.abs(z)**2*z + G*(Cs[k]@z - degs[k]*z)) + sq*(rng.standard_normal(n)+1j*rng.standard_normal(n))
        if t % every == 0: xs.append(z.real.copy())
    return np.array(xs).T, switches

def split_half(x, seed):
    ev = events(x); h1, h2 = ev[:len(ev)//2], ev[len(ev)//2:]
    l1, _ = detect(h1, seed); l2, _ = detect(h2, seed + 1)
    W = infer_cond(h1); rng = np.random.default_rng(seed)
    return ari(l1, l2), E_norm(h2, W, l1, rng), E_norm(h2, W, l2, rng)

agg = {}
print(f"{'subj':<8}{'condition':<16}{'switches':>9}{'ARI l1~l2':>10}{'E(l1)':>7}{'E(l2)':>7}")
for s in b.SUBJECTS:
    C, _ = b.load(s); Ch = C + 0.05 * H
    reps = [labels_of(x) for x in b.SUBJECTS if x != s]
    co = sum((l[:, None] == l[None, :]).astype(float) for l in reps) / 3; np.fill_diagonal(co, 0)
    cons = louvain(co, 1.0, 21)
    conds = {"no gate": ([Ch], 0), "fixed gate": ([gate(Ch, cons)], 0),
             "switch 120 s": ([gate(Ch, l) for l in reps], 120.0), "switch 30 s": ([gate(Ch, l) for l in reps], 30.0)}
    for name, (Cs, dwell) in conds.items():
        r = []
        for seed in (91, 92):
            x, sw = sim_switch(Cs, dwell, seed); r.append((sw,) + split_half(x, seed))
        m = np.mean(r, 0); agg.setdefault(name, []).append(m)
        print(f"{s:<8}{name:<16}{m[0]:>9.0f}{m[1]:>10.2f}{m[2]:>7.2f}{m[3]:>7.2f}", flush=True)
print("\nmeans (empirical tick 39: ARI 0.09, E(l1) 0.49, E(l2) 0.42)")
for name, rows in agg.items():
    m = np.mean(rows, 0); print(f"  {name:<14} ARI {m[1]:.2f}  E(l1) {m[2]:.2f}  E(l2) {m[3]:.2f}")
