"""Tick 72: replicate tick 71 on seeds 2 and 3 for the two extreme rules (lagged vs synchronous+competitive+inhibition)."""
import numpy as np, networkx as nx
from tick70 import run, N
from tick71 import simulate, E_norm

print(f"{'rule':<16}{'seed':>5}{'parts':>6}{'learned':>9}{'initial':>9}{'gain':>7}")
for variant in ("lagged", "sync+norm+inh"):
    for seed in (2, 3):
        _, W, gain = run(variant, seed, return_w=True)
        lab = np.empty(N, int)
        for k, c in enumerate(nx.community.louvain_communities(nx.from_numpy_array((W + W.T) / 2), weight="weight", seed=seed)): lab[list(c)] = k
        A0 = nx.to_numpy_array(nx.erdos_renyi_graph(N, 8/N, seed=seed)) / 8.0
        rng = np.random.default_rng(seed)
        el, e0 = E_norm(simulate(W, gain, seed), W, lab, rng), E_norm(simulate(A0, 0.9, seed), A0, lab, rng)
        print(f"{variant:<16}{seed:>5}{lab.max()+1:>6}{el:>9.2f}{e0:>9.2f}{el-e0:>7.2f}", flush=True)
