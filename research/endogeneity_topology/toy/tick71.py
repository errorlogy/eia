"""Tick 71: are the weakly self-organised modules (tick 70) functional sub-agents? After 30k ticks of learning,
freeze W, simulate 4000 ticks, and compute E_norm (true W attribution) of the Louvain partition of the learned
weights, vs the same partition size on the initial (unlearned) weights. 1 seed per rule."""
import numpy as np, networkx as nx
import topo_endo as te
from tick70 import run, N

def simulate(W, gain, seed, T=4000):
    rng = np.random.default_rng(seed + 77)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        inp = (gain * W) @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*np.clip(inp, 0, None)*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out[500:]

def E(sp, W, lab):
    P = sp[:-1].astype(float); tot = P @ W.T; ins = P @ (W * (lab[:, None] == lab[None, :])).T
    return ((tot <= 1e-12) | (ins >= 0.5 * tot))[sp[1:]].mean()

def E_norm(sp, W, lab, rng):
    en = np.mean([E(sp, W, lab[rng.permutation(N)]) for _ in range(5)]); return (E(sp, W, lab) - en) / (1 - en)

print(f"{'rule':<16}{'#parts':>7}{'E_norm learned W':>18}{'E_norm initial W':>18}")
for variant in ("lagged", "sync+norm", "sync+norm+inh"):
    _, W, gain = run(variant, 1, return_w=True)
    Ws = (W + W.T) / 2
    lab = np.empty(N, int)
    for k, c in enumerate(nx.community.louvain_communities(nx.from_numpy_array(Ws), weight="weight", seed=1)): lab[list(c)] = k
    A0 = nx.to_numpy_array(nx.erdos_renyi_graph(N, 8/N, seed=1)) / 8.0
    rng = np.random.default_rng(1)
    e_l = E_norm(simulate(W, gain, 1), W, lab, rng)
    e_0 = E_norm(simulate(A0, 0.9, 1), A0, lab, rng)
    print(f"{variant:<16}{lab.max()+1:>7}{e_l:>18.2f}{e_0:>18.2f}", flush=True)
