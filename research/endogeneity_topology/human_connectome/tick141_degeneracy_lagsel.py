"""Tick 141: is B9 (degenerate empirical boundaries) robust to a lag-selective detector (tick 140) instead of the summed
lags 1-3 TR used before? Split-half partitions per subject (7), Louvain on the lag-selective graph (best lag 1..3 per pair),
resolution chosen by E_norm gain on the half's own second part; split-half ARI and held-out E_norm (lag-selective attribution)."""
import numpy as np, networkx as nx
import brain_eia as b
from tick14_boundaries import ari
from tick15_empirical import events
from tick81_initiators_7subj import SUBJ, load
L = 3

def lagsel(ev):
    S = ev.astype(float); T, n = S.shape; r = S.mean(0); Ks = []
    for l in range(1, L + 1):
        K = (S[:-l].T @ S[l:]).T - np.outer(r, r) * (T - l); np.fill_diagonal(K, 0); Ks.append(K)
    Ks = np.stack(Ks); best = Ks.argmax(0) + 1; Kb = np.clip(Ks.max(0), 0, None); B = np.zeros((n, n))
    for i in range(n):
        js = np.argsort(Kb[i])[-10:]; js = js[Kb[i, js] > 0]
        if len(js) == 0: continue
        Xi = np.column_stack([np.ones(T - L), S[L-1:T-1, i]] + [S[L - best[i, j]: T - best[i, j], j] for j in js])
        B[i, js] = np.clip(np.linalg.lstsq(Xi, S[L:, i], rcond=None)[0][2:], 0, None)
    thr = np.percentile(B[B > 0], 80) if (B > 0).any() else 0
    return np.where(B >= thr, B, 0), best

def E(ev, W, best, lab):
    S = ev.astype(float); T = len(S); tot = np.zeros((T, 94)); ins = np.zeros((T, 94)); same = lab[:, None] == lab[None, :]
    for l in range(1, L + 1):
        M = np.where(best == l, W, 0); sh = np.vstack([np.zeros((l, 94)), S[:T - l]]); tot += sh @ M.T; ins += sh @ (M * same).T
    return ((tot <= 1e-12) | (ins >= 0.5 * tot))[ev].mean()

def E_norm(ev, W, best, lab, rng):
    en = np.mean([E(ev, W, best, lab[rng.permutation(94)]) for _ in range(5)]); return (E(ev, W, best, lab) - en) / (1 - en)

def detect(ev, seed):
    tr, te = ev[:len(ev)//2], ev[len(ev)//2:]; W, best = lagsel(tr); rng = np.random.default_rng(seed); G = nx.from_numpy_array(W + W.T); top = None
    for res in [0.5, 0.8, 1, 1.5, 2, 3]:
        lab = np.empty(94, int)
        for k, c in enumerate(nx.community.louvain_communities(G, weight="weight", resolution=res, seed=seed)): lab[list(c)] = k
        sc = E_norm(te, W, best, lab, rng)
        if top is None or sc > top[0]: top = (sc, lab)
    return top[1]

rows = []
for s in SUBJ:
    _, tc = load(s); ev = events(tc); h1, h2 = ev[:len(ev)//2], ev[len(ev)//2:]
    l1, l2 = detect(h1, 41), detect(h2, 42); W, best = lagsel(h1)
    rows.append((ari(l1, l2), E_norm(h2, W, best, l1, np.random.default_rng(1))))
    print(f"{s}: split-half ARI {rows[-1][0]:+.2f}   held-out E_norm {rows[-1][1]:.2f}", flush=True)
m = np.mean(rows, 0); print(f"mean: ARI {m[0]:.2f} (tick 96 conditional: 0.04), held-out E_norm {m[1]:.2f} (tick 96: 0.38)")
