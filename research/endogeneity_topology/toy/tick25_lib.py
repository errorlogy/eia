"""Helpers shared by tick 25/26: SBM generator and signed (inhibitory) coupling."""
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs

N = 1000


def sbm(seed, mu, size=100, deg=5.0):
    k = N//size; p_in = deg*(1-mu)/(size-1); p_out = deg*mu/(N-size)
    g = nx.stochastic_block_model([size]*k, [[p_in if i == j else p_out for j in range(k)] for i in range(k)], seed=seed, sparse=True)
    return nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float), np.arange(N)//size

def signed(A, truth, cond, seed):
    A = A.tocoo(); w = np.ones_like(A.data)
    if cond == "cross_inh": w[truth[A.row] != truth[A.col]] = -1
    if cond == "dale20":
        inh = np.random.default_rng(seed+7).random(N) < 0.2; w[inh[A.col]] = -1     # col = presynaptic j
    S = sps.csr_matrix((w, (A.row, A.col)), shape=A.shape)
    Wp = S.maximum(0); lam = abs(eigs(Wp, k=1, which="LM", return_eigenvectors=False)[0])
    return S/lam, Wp/lam
