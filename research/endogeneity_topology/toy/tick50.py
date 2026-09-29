"""Tick 50: how much recurrence does collective endogeneity need? Strict DAG (i->j, i<j) where a fraction f
of edges is reversed (creating cycles). Mean branching g; metrics: loop gain rho(W)/g, rate x base over g,
max step jump (onset sharpness). f in {0, .02, .05, .1, .2, .5}. 2 seeds."""
import numpy as np
import scipy.sparse as sps

import topo_endo as te

N = te.N = 1000


def run(W, seed, T=3000):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros(T)
    for t in range(T):
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s.mean()
    return out


def graph(f, seed, k=4):
    rng = np.random.default_rng(seed)
    A = np.triu(rng.random((N, N)) < 2*k/N, 1)
    rev = A & (rng.random((N, N)) < f)
    return (A & ~rev).astype(float) + rev.T.astype(float)


if __name__ == "__main__":
    gs = [0.6, 0.8, 1.0, 1.2, 1.5, 2.0]
    base = run(sps.csr_matrix((N, N)), 1)[500:].mean()
    print(f"{'f':>5}{'rho/g':>7} | " + " ".join(f"{'g='+str(g):>7}" for g in gs) + " | max jump")
    for f in [0.0, 0.02, 0.05, 0.1, 0.2, 0.5]:
        rs, rho = [], []
        for seed in (1, 2):
            A = graph(f, seed); W1 = A / A.sum(1).mean()
            rho.append(np.max(np.abs(np.linalg.eigvals(W1))))
            rs.append([run(sps.csr_matrix(W1 * g), seed)[500:].mean() / base for g in gs])
        r = np.mean(rs, 0)
        print(f"{f:>5.2f}{np.mean(rho):>7.2f} | " + " ".join(f"{x:>7.1f}" for x in r) + f" | {np.max(np.diff(r)):.1f}", flush=True)
