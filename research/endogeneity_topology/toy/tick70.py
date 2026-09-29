"""Tick 70: competitive plasticity — can sub-agents self-organise with (i) synchronous (same-window) Hebbian
co-activation instead of lagged, (ii) row+column normalisation (each unit's input AND output budgets fixed:
competition), (iii) plus global inhibition -gamma*mean(s)? ER support N=500 degree 8, rate homeostasis, 30k ticks,
eta 0.05, 2 seeds. Metric: Louvain Q of weights vs shuffled-weight null (Q - Qnull > 0 = emergent modularity)."""
import numpy as np, networkx as nx
import topo_endo as te
N = te.N = 500

def run(variant, seed, T=30000, win=20, eta=0.05):
    rng = np.random.default_rng(seed)
    A = nx.to_numpy_array(nx.erdos_renyi_graph(N, 8/N, seed=seed)); mask = A > 0
    W = A / 8.0; tot = W.sum(); gain = 0.9
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N)
    prev = np.zeros(N); C = np.zeros((N, N)); act = []; out = []
    gamma = 3.0 if variant == "sync+norm+inh" else 0.0
    for t in range(T):
        inp = (gain * W) @ s - gamma * s.mean()
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*np.clip(inp, 0, None)*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        prev = s; s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); act.append(s.mean())
        C += np.outer(s, prev) if variant == "lagged" else np.outer(s, s + prev)
        if (t + 1) % win == 0:
            Cm = C[mask].mean(); W = np.where(mask, np.clip(W + eta * 0.01 * (C - Cm) / (win * 0.03), 0, None), 0); C[:] = 0
            if variant == "lagged":
                W = W / (W.sum(1, keepdims=True) + 1e-12) * (A.sum(1, keepdims=True) / 8.0)
            else:
                for _ in range(3):   # Sinkhorn-like: fix both input and output budgets
                    W = W / (W.sum(1, keepdims=True) + 1e-12) * (A.sum(1, keepdims=True) / 8.0)
                    W = W / (W.sum(0, keepdims=True) + 1e-12) * (A.sum(0, keepdims=True) / 8.0)
            r = np.mean(act[-win:]); gain = float(np.clip(gain * (1 + 0.05 * (0.03 - r) / 0.03), 0.3, 3.0))
        if (t + 1) % 15000 == 0:
            Ws = (W + W.T) / 2; G = nx.from_numpy_array(Ws)
            Q = nx.community.modularity(G, nx.community.louvain_communities(G, weight="weight", seed=seed), weight="weight")
            vals = Ws[np.triu(mask, 1)]; Wn = np.zeros_like(Ws); Wn[np.triu(mask, 1)] = rng.permutation(vals); Wn = Wn + Wn.T
            Gn = nx.from_numpy_array(Wn); Qn = nx.community.modularity(Gn, nx.community.louvain_communities(Gn, weight="weight", seed=seed), weight="weight")
            out.append((t + 1, Q, Qn, vals.std() / vals.mean(), gain, np.mean(act[-1000:])))
    return out

print(f"{'variant':<16}{'seed':>5}{'t':>7}{'Q':>7}{'Q null':>8}{'Q-Qn':>7}{'w CV':>6}{'gain':>6}{'rate':>7}")
for variant in ("lagged", "sync+norm", "sync+norm+inh"):
    for seed in (1, 2):
        for t, Q, Qn, cv, g, r in run(variant, seed):
            print(f"{variant:<16}{seed:>5}{t:>7}{Q:>7.3f}{Qn:>8.3f}{Q-Qn:>7.3f}{cv:>6.2f}{g:>6.2f}{r:>7.3f}", flush=True)
