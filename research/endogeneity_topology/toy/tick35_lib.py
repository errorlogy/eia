"""Helpers from tick 35: pairwise and conditional blind attribution."""
import numpy as np, scipy.sparse as sps

N = 1000


def pairwise(sp):
    S = sps.csr_matrix(sp.astype(float)); r = sp.mean(0)
    K = (S[:-1].T @ S[1:]).toarray().T - np.outer(r, r) * (len(sp) - 1)
    np.fill_diagonal(K, 0); return np.clip(K, 0, None)

def top10(K):
    thr = np.percentile(K[K > 0], 90); return sps.csr_matrix(np.where(K >= thr, K, 0))

def conditional(sp, K, cand=20):
    X = sp[:-1].astype(float); Y = sp[1:].astype(float); B = np.zeros((N, N))
    for i in range(N):
        if Y[:, i].sum() < 3: continue
        js = np.argsort(K[i])[-cand:]; js = js[K[i, js] > 0]
        cols = np.concatenate([[i], js]); Xi = np.column_stack([np.ones(len(X)), X[:, cols]])
        coef = np.linalg.lstsq(Xi, Y[:, i], rcond=None)[0][2:]
        B[i, js] = np.clip(coef, 0, None)
    return B
