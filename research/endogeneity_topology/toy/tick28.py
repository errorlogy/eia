"""Tick 28: mechanism of the floor-holder sign flip under lateral inhibition (tick 27).
SBM 10x100, mu=0.2, cross-module inhibitory, rate-matched. For t0 in {1000,1100,1200,1300} and 10 seeds,
boost (u=1) the current floor holder and one random non-holder. Record, vs exact twin, over 300 ticks:
target initiatives per 25-tick bin, target mean uncertainty u, and initiatives of the rest."""
import numpy as np, scipy.sparse as sps
import topo_endo as te
from tick25_lib import sbm, signed
from tick26 import sim as sim_plain

N, H, BIN = 1000, 300, 25
def sim_rec(W, seed, T, target, t0=None):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N)
    spk = np.zeros((T, N), bool); um = np.zeros(T)
    for t in range(T):
        if t0 is not None and t == t0: u[target] = 1.0
        xi = rng.standard_normal(N); inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*xi - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1)
        spk[t] = s > 0; um[t] = u[target].mean()
    return spk, um

res = {"holder": [], "other": []}
for seed in range(1, 11):
    A, truth = sbm(seed, 0.2); S1, _ = signed(A, truth, "cross_inh", seed)
    lo, hi = 0.5, 3.0
    for _ in range(11):
        m_ = (lo+hi)/2; lo, hi = (m_, hi) if sim_plain(S1*m_, seed, T=1000)[500:].mean() < 0.03 else (lo, m_)
    W = sps.csr_matrix(S1*(lo+hi)/2)
    rng = np.random.default_rng(seed + 100)
    for t0 in (1000, 1100, 1200, 1300):
        T = t0 + H
        base_spk, _ = sim_rec(W, seed, T, np.flatnonzero(truth == 0))
        pre = np.array([base_spk[t0-20:t0, truth == k].sum() for k in range(10)])
        if pre.sum() == 0: continue
        top = int(np.argmax(pre)); oth = int(rng.choice([k for k in range(10) if k != top]))
        for tag, k in (("holder", top), ("other", oth)):
            tgt = np.flatnonzero(truth == k)
            _, u_tw = sim_rec(W, seed, T, tgt)
            spk, u_pe = sim_rec(W, seed, T, tgt, t0)
            d_in = (spk[t0:, tgt].sum(1).astype(int) - base_spk[t0:, tgt].sum(1)).reshape(-1, BIN).sum(1)
            d_out = (spk[t0:][:, truth != k].sum(1).astype(int) - base_spk[t0:][:, truth != k].sum(1)).reshape(-1, BIN).sum(1)
            du = (u_pe[t0:] - u_tw[t0:]).reshape(-1, BIN).mean(1)
            res[tag].append((d_in, d_out, du, pre[k] / pre.sum()))
bins = [f"{i*BIN}-{(i+1)*BIN}" for i in range(H//BIN)]
for tag, r in res.items():
    di = np.array([x[0] for x in r]); do = np.array([x[1] for x in r]); du = np.array([x[2] for x in r])
    print(f"\n[{tag}] n={len(r)}  pre-share {np.mean([x[3] for x in r]):.2f}  total d_in {di.sum(1).mean():.1f} (sd {di.sum(1).std():.1f})  total d_out {do.sum(1).mean():.1f}")
    print("  bin       " + " ".join(f"{b:>8}" for b in bins[:8]))
    print("  d_in      " + " ".join(f"{x:>8.1f}" for x in di.mean(0)[:8]))
    print("  d_out     " + " ".join(f"{x:>8.1f}" for x in do.mean(0)[:8]))
    print("  d_u(tgt)  " + " ".join(f"{x:>8.3f}" for x in du.mean(0)[:8]))
