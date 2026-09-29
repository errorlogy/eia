"""Tick 69: can sub-agents self-organise? ER support (N=500, degree 8), plastic weights:
  every 20 ticks: w_ij += eta * (C_ij - <C>) where C_ij = co-activation count (j at t-1, i at t) in the window,
  clip >= 0, row-normalise to the initial row sum; global gain adapted to keep rate ~0.03 (homeostasis).
Track over 30000 ticks: Louvain modularity Q of the weight graph vs Q of weight-shuffled null, number of
communities, and the true-W E_norm of the Louvain partition. 2 seeds; eta in {0 (control), 0.02, 0.05}."""
import numpy as np, networkx as nx, scipy.sparse as sps
import topo_endo as te
N = te.N = 500

def run(eta, seed, T=30000, win=20):
    rng = np.random.default_rng(seed)
    A = nx.to_numpy_array(nx.erdos_renyi_graph(N, 8/N, seed=seed)); mask = A > 0
    W = A / 8.0; row0 = W.sum(1, keepdims=True) + 1e-12; gain = 0.9
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N)
    prev = np.zeros(N); C = np.zeros((N, N)); hist, act = [], []
    for t in range(T):
        inp = (gain * W) @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        prev = s; s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1)
        act.append(s.mean())
        if eta: C += np.outer(s, prev)
        if (t + 1) % win == 0:
            if eta:
                Cm = C[mask].mean(); W = np.where(mask, np.clip(W + eta * (C - Cm) / (win * 0.03 + 1e-9) * 0.01, 0, None), 0)
                W = W / (W.sum(1, keepdims=True) + 1e-12) * row0; C[:] = 0
            r = np.mean(act[-win:]); gain = float(np.clip(gain * (1 + 0.05 * (0.03 - r) / 0.03), 0.3, 2.0))
        if (t + 1) % 10000 == 0:
            Ws = (W + W.T) / 2; G = nx.from_numpy_array(Ws)
            comms = nx.community.louvain_communities(G, weight="weight", seed=seed)
            Q = nx.community.modularity(G, comms, weight="weight")
            vals = Ws[np.triu(mask, 1)]; perm = rng.permutation(vals); Wn = np.zeros_like(Ws); Wn[np.triu(mask, 1)] = perm; Wn = Wn + Wn.T
            Gn = nx.from_numpy_array(Wn); Qn = nx.community.modularity(Gn, nx.community.louvain_communities(Gn, weight="weight", seed=seed), weight="weight")
            hist.append((t + 1, Q, Qn, len(comms), gain, np.mean(act[-1000:]), float(Ws[np.triu(mask,1)].std() / Ws[np.triu(mask,1)].mean())))
    return hist

print(f"{'eta':>5}{'seed':>5}{'t':>7}{'Q':>7}{'Q null':>8}{'#comm':>7}{'gain':>6}{'rate':>7}{'w CV':>6}")
for eta in (0.0, 0.02, 0.05):
    for seed in (1, 2):
        for row in run(eta, seed):
            print(f"{eta:>5}{seed:>5}{row[0]:>7}{row[1]:>7.3f}{row[2]:>8.3f}{row[3]:>7}{row[4]:>6.2f}{row[5]:>7.3f}{row[6]:>6.2f}", flush=True)
