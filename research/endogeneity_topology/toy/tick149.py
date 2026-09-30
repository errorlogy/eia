"""Tick 149: can a workspace layer give the hierarchy back its combinatorial novelty (A39) without losing containment?
hier-modular + hub workspace layer (tick 67 layers) w in {0, 0.2, 0.4}; rate-matched; 15 000 ticks; distinct multi-block
patterns, late discovery rate, entropy. 2 seeds."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
from tick148 import sim, discovery, build, N, T
from tick67 import layers
from tick142 import sim as sim_route

print(f"{'w':>5}{'distinct patterns':>18}{'late new / 1000t':>18}{'entropy':>9}")
for w in (0.0, 0.2, 0.4):
    rows = []
    for seed in (1, 2):
        H = nx.to_scipy_sparse_array(build("hier_modular", seed)[0], nodelist=range(N), format="csr", dtype=float)
        H = H / abs(eigs(H, k=1, which="LM", return_eigenvectors=False)[0]); _, B = layers(seed)
        lo, hi = 0.3, 1.5
        for _ in range(9):
            mid = (lo+hi)/2; lo, hi = (mid, hi) if sim_route(sps.csr_matrix(H*mid + B*w), seed, 0.0, 1500)[0].mean() < 0.03 else (lo, mid)
        rows.append(discovery(sim(sps.csr_matrix(H*(lo+hi)/2 + B*w), seed, T)[500:]))
    m = np.mean(rows, 0); print(f"{w:>5}{m[0]:>18.0f}{m[1]:>18.2f}{m[2]:>9.2f}", flush=True)
print("reference (tick 148): SBM 637 / 20.6 / 7.56; hier 248 / 7.8 / 6.67")
