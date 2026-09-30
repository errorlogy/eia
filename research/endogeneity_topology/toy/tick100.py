"""Tick 100: what does the agent depend on — the world's CONTINGENCY on its actions, or just input volume?
Conditions (w=1, D=20): contingent echo (tick 98); cut world; non-contingent replay = the echo stream recorded from the
contingent run, time-shuffled in 50-tick blocks and replayed regardless of what the agent does. SBM and ER agents, 3 seeds."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
import topo_endo as te
from tick98 import NA, motor, sens

def sim(W, seed, mode, T=3000, D=20, p=0.8, replay=None):
    rng = np.random.default_rng(seed); rec = np.zeros((T, 100), bool)
    d = rng.uniform(0, .3, NA); u = rng.uniform(.2, .6, NA); s = np.zeros(NA); refr = np.zeros(NA); hist = np.zeros((T, NA), bool)
    for t in range(T):
        echo = np.zeros(NA); r = rng.random(100)                    # draw every tick: same stream in all modes
        if mode == "contingent" and t >= D: rec[t] = hist[t - D, motor] & (r < p)
        elif mode == "replay": rec[t] = replay[t]
        echo[sens] = rec[t]
        inp = W @ s + echo
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(NA) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); hist[t] = s > 0
    return hist[500:], rec

def agent(kind, seed):
    if kind == "SBM":
        return nx.stochastic_block_model([100]*10, [[5*0.9/99 if i == j else 5*0.1/900 for j in range(10)] for i in range(10)], seed=seed, sparse=True)
    return nx.erdos_renyi_graph(NA, 5/NA, seed=seed)

if __name__ == "__main__":
    print(f"{'agent':<5}{'kept: cut world':>16}{'kept: non-contingent replay':>29}{'contingency share of support':>30}")
    for kind in ("SBM", "ER"):
        rows = []
        for seed in (1, 2, 3):
            A = nx.to_scipy_sparse_array(agent(kind, seed), nodelist=range(NA), format="csr", dtype=float); A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
            lo, hi = 0.3, 1.5
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(A1*mid), seed, "contingent", 1500)[0].mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(A1*(lo+hi)/2)
            full, rec = sim(W, seed, "contingent")
            blocks = np.array_split(np.arange(len(rec)), len(rec) // 50); order = np.random.default_rng(seed + 5).permutation(len(blocks))
            shuffled = np.concatenate([rec[blocks[i]] for i in order])
            cut, _ = sim(W, seed, "cut"); rep, _ = sim(W, seed, "replay", replay=shuffled)
            k_cut, k_rep = cut.mean() / full.mean(), rep.mean() / full.mean()
            rows.append((k_cut, k_rep, (1 - k_rep) / max(1 - k_cut, 1e-9)))
        m = np.mean(rows, 0); print(f"{kind:<5}{m[0]:>16.2f}{m[1]:>29.2f}{m[2]:>30.2f}", flush=True)
