"""Tick 121: dominance-gated Governor. The per-motive cap term kp*max(0, S_m - 0.15) is applied only to motives whose slow
share S_m (tau 1000) exceeds a dominance gate of 0.25; global budget loop as tick 93.
Case A: SBM with a strong generator (module 0 x2.5) — does the gated cap still hold it down, and keep others controllable?
Case B: balanced hier + workspace — is per-motive controllability preserved (tick 120 lost it)? 6 seeds x 3 motives."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
from tick92 import N, mods, T, T0, M
from tick118 import build, layers

def sim(W, alpha, seed, mode, boost=None, kp=1.5, kg=2.0, ki=0.002, tau=1000.0, gate=0.25):
    rng = np.random.default_rng(seed); S = np.full(10, 0.1); R = 0.03; I = 0.0
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        if boost is not None and t == T0: u[boost] = 1.0
        if mode == "none": thr = te.THETA
        else:
            cap = kp * np.maximum(0, S - 0.15)
            if mode == "gated": cap = np.where(S > gate, cap, 0.0)
            thr = (te.THETA + cap + kg * (R - 0.03) + I)[mods]
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + alpha*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > thr) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
        tot = s.sum()
        if tot: S += (s @ M / tot - S) / tau
        R += (s.mean() - R) / tau
        if mode != "none": I = float(np.clip(I + ki * (s.mean() - 0.03), -0.3, 0.3))
    return out

z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
def case(kind, mode):
    a, shares = [], []
    for seed in range(1, 7):
        alpha = np.full(N, te.ALPHA)
        if kind == "A":
            g = nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
            A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float); A = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0]); B = 0 * A; wb = 0.0
            alpha[mods == 0] *= 2.5
        else:
            A = nx.to_scipy_sparse_array(build("hier_modular", seed)[0], nodelist=range(N), format="csr", dtype=float)
            A = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0]); _, B = layers(seed); wb = 0.4
        lo, hi = 0.3, 1.4
        for _ in range(10):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A*mid + B*wb), alpha, seed, "none")[500:1500].mean() < 0.03 else (lo, mid)
        W = sps.csr_matrix(A*(lo+hi)/2 + B*wb); tw = sim(W, alpha, seed, mode)
        shares.append(tw[1000:T0, mods == 0].sum() / tw[1000:T0].sum())
        for m in (2, 5, 8):
            ins = mods == m; pe = sim(W, alpha, seed, mode, boost=np.flatnonzero(ins)); a.append(int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum()))
    a = np.array(a); return np.mean(shares), a.mean(), z(a)

print(f"{'case':<32}{'module-0 share':>15}{'d self':>8}{'z':>7}")
for kind, label in (("A", "A: strong generator"), ("B", "B: balanced hier+workspace")):
    for mode in ("none", "always", "gated"):
        sh, d, zz = case(kind, mode)
        print(f"{label + ' / ' + mode:<32}{sh:>15.2f}{d:>8.1f}{zz:>7.2f}", flush=True)
