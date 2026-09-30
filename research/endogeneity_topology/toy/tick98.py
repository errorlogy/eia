"""Tick 98: agent-world loop. Agent = SBM 10x100 (mu 0.1). World = 100 relay units: world unit k echoes the initiative of
agent 'motor' unit k (units 900-999) after delay D ticks with prob p, and feeds agent 'sensory' unit k (units 0-99) with
weight w. No external triggers (X=0); the world only reflects the agent's own actions.
Measures (rate-matched on the agent): share of agent initiatives whose inferred cause includes world input (true W),
agent independence = agent activity kept when the world->agent link is cut, for w in {0, 0.5, 1.0}, D=20. 3 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
NA = 1000; motor = np.arange(900, 1000); sens = np.arange(0, 100)

def sim(W, seed, w_world, T=3000, D=20, p=0.8, cut=False):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, NA); u = rng.uniform(.2, .6, NA); s = np.zeros(NA); refr = np.zeros(NA)
    hist = np.zeros((T, NA), bool); world_in = np.zeros((T, NA)); via = []
    for t in range(T):
        echo = np.zeros(NA)
        if t >= D and not cut:
            fired = hist[t - D, motor] & (rng.random(100) < p)
            echo[sens] = w_world * fired
        inp = W @ s + echo
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(NA) - .8*s, 0, 1)
        new = ((d > te.THETA) & (refr <= 0)).astype(float)
        if new.any(): via.append(((echo > 0) & (new > 0)).sum() / new.sum())
        s = new; refr = np.where(s > 0, 5, refr-1); hist[t] = s > 0
    return hist[500:], np.mean(via) if via else 0.0

if __name__ == "__main__":
    print(f"{'w_world':>8}{'agent rate':>11}{'initiatives touched by world':>30}{'independence (world cut)':>26}")
    for w in (0.0, 0.5, 1.0):
        rows = []
        for seed in (1, 2, 3):
            g = nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
            A = nx.to_scipy_sparse_array(g, nodelist=range(NA), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.3, 1.5
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), seed, w, 1500)[0].mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(A1*(lo+hi)/2)
            full, via = sim(W, seed, w); cut, _ = sim(W, seed, w, cut=True)
            rows.append((full.mean(), via, cut.mean() / full.mean()))
        m = np.mean(rows, 0); print(f"{w:>8}{m[0]:>11.3f}{m[1]:>30.3f}{m[2]:>26.2f}", flush=True)
