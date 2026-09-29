"""Tick 66: higher-order (simplicial) interactions. Input to unit i = pairwise W@s + lam * (active triangles
through i) / norm — a triangle (i,j,k) contributes only when BOTH j and k fired (coincidence detection).
Graph: small-world ring k=6 (many triangles), N=1000. Sweep pairwise gain g at lam in {0, 0.5, 1.0}.
Metrics: rate x base, max step jump (onset sharpness), hysteresis (up-sweep vs down-sweep rate at same g)."""
import numpy as np, networkx as nx, scipy.sparse as sps
import topo_endo as te
N = te.N = 1000

g0 = nx.watts_strogatz_graph(N, 6, 0.05, seed=1)
A = nx.to_scipy_sparse_array(g0, nodelist=range(N), format="csr", dtype=float)
tri = [(i, j, k) for i in range(N) for j in g0[i] for k in g0[i] if j < k and g0.has_edge(j, k)]
TI = np.array(tri); ntri = np.bincount(TI[:, 0], minlength=N).astype(float); ntri[ntri == 0] = 1
W1 = A / A.sum(1).mean()

def run(g, lam, seed, T=2500, state=None):
    rng = np.random.default_rng(seed)
    if state is None:
        d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N)
    else:
        d, u, s, refr = (x.copy() for x in state)
    out = np.zeros(T)
    for t in range(T):
        inp = (W1 * g) @ s
        if lam:
            both = s[TI[:, 1]] * s[TI[:, 2]]
            inp = inp + lam * np.bincount(TI[:, 0], weights=both, minlength=N) / ntri
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s.mean()
    return out, (d, u, s, refr)

base = run(0.0, 0.0, 1)[0][500:].mean()
gs = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
print(f"{'lam':>4} | up-sweep rate x base " + " ".join(f"{g:>6}" for g in gs) + " | max jump | hysteresis area")
for lam in (0.0, 0.5, 1.0):
    up, st = [], None
    for g in gs:
        o, st = run(g, lam, 1, state=st); up.append(o[500:].mean() / base)
    down = []
    for g in reversed(gs):
        o, st = run(g, lam, 1, state=st); down.append(o[500:].mean() / base)
    down = down[::-1]
    hyst = float(np.sum(np.array(down) - np.array(up)))
    print(f"{lam:>4} | {'':>20}" + " ".join(f"{x:>6.1f}" for x in up) + f" | {np.max(np.diff(up)):>8.1f} | {hyst:>8.1f}")
    print(f"{'':>4} | {'down-sweep':>20}" + " ".join(f"{x:>6.1f}" for x in down), flush=True)
