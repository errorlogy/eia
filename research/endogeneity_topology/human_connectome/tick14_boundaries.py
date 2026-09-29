"""Tick 14: blind self-boundary detection on the human-connectome Hopf model.
Events = onsets of region envelope above its own 90th pct (sampled every 0.2 s, 1800 s).
Directed lagged excess (lags 1..5 samples) -> Louvain -> compare with EIA module map,
hemispheres, and Louvain on the structural connectome. E-profile blind, found vs null."""
import json, zlib
import numpy as np, networkx as nx, scipy.sparse as sps
from math import comb
import brain_eia as b


def ari(a, c):
    _, ai = np.unique(a, return_inverse=True); _, ci = np.unique(c, return_inverse=True)
    M = np.zeros((ai.max()+1, ci.max()+1), int); np.add.at(M, (ai, ci), 1)
    s = sum(comb(int(x), 2) for x in M.ravel()); sa = sum(comb(int(x), 2) for x in M.sum(1)); sc = sum(comb(int(x), 2) for x in M.sum(0))
    e = sa * sc / comb(len(a), 2); return (s - e) / (0.5 * (sa + sc) - e)

G = json.loads(open(b.HERE / "results.json").read())["G_star"]
DT, SAMPLE, T, LAGS = 0.1, 2, 1800.0, 5
MODLAB = np.full(94, -1)
for k, (m, idx) in enumerate(b.IDX.items()): MODLAB[idx] = k
HEMI = np.array([0 if l.endswith("_L") else 1 for l in b.LABELS])

def sim(C, w, a_vec, seed):
    rng = np.random.default_rng(seed); n = 94; omega = 2*np.pi*w; deg = C.sum(1); sq = np.sqrt(DT)*0.02
    z = 0.1*(rng.standard_normal(n)+1j*rng.standard_normal(n)); env = []
    for t in range(int(T/DT)):
        z = z + DT*((a_vec+1j*omega)*z - np.abs(z)**2*z + G*(C@z-deg*z)) + sq*(rng.standard_normal(n)+1j*rng.standard_normal(n))
        if t % SAMPLE == 0: env.append(np.abs(z))
    return np.array(env)                                       # (time, 94)

def onsets(env):
    hi = env > np.percentile(env, 90, axis=0)
    return hi & ~np.vstack([np.zeros((1, 94), bool), hi[:-1]])

def infer(ev):
    r = ev.mean(0); K = np.zeros((94, 94)); E = ev.astype(float)
    for L in range(1, LAGS+1):
        K += (E[:-L].T @ E[L:]).T - np.outer(r, r)*(len(ev)-L)   # K[i,j]: j -> i
    np.fill_diagonal(K, 0); K = np.clip(K, 0, None)
    return np.where(K >= np.percentile(K[K > 0], 80), K, 0)

def E_blind(ev, Wh, lab):
    E = ev.astype(float); par = sum(np.vstack([np.zeros((L, 94)), E[:-L]]) for L in range(1, LAGS+1))
    tot = par @ Wh.T; same = (lab[:, None] == lab[None, :]); ins = par @ (Wh*same).T
    return ((tot <= 1e-12) | (ins >= 0.5*tot))[ev].mean()

def louvain(Wsym, res, seed):
    lab = np.empty(94, int)
    for k, c in enumerate(nx.community.louvain_communities(nx.from_numpy_array(Wsym), weight="weight", resolution=res, seed=seed)): lab[list(c)] = k
    return lab

subj = {s: b.load(s) for s in b.SUBJECTS}
w = np.mean([b.peak_freqs(tc) for _, tc in subj.values()], axis=0)
a_hom = np.full(94, -0.02)
a_het = a_hom.copy(); a_het[b.IDX["SEN"]] = -0.04; a_het[np.concatenate([b.IDX["DMN"], b.IDX["FPN"], b.IDX["VAL"]])] = -0.005
known = MODLAB >= 0
print(f"{'variant':<6}{'subj':<8}{'#parts':>7}{'E_found':>8}{'E_null':>7}{'E_EIAmods':>10}{'ARI_EIA':>8}{'ARI_hemi':>9}{'ARI_SC':>7}")
out = []
for variant, a_vec in [("hom", a_hom), ("het", a_het)]:
    for s, (C, _) in subj.items():
        seed = zlib.crc32(repr((s, variant, 14)).encode()); rng = np.random.default_rng(seed)
        ev = onsets(sim(C, w, a_vec, seed)); tr, te_ = ev[:len(ev)//2], ev[len(ev)//2:]
        Wh = infer(tr); best = None
        for res in [0.5, 0.8, 1, 1.5, 2, 3]:
            lab = louvain(Wh + Wh.T, res, seed)
            sc = E_blind(te_, Wh, lab) - E_blind(te_, Wh, lab[rng.permutation(94)])
            if best is None or sc > best[0]: best = (sc, lab)
        lab = best[1]; sclab = louvain(C, 1.0, seed)
        eia = MODLAB.copy(); eia[~known] = 100 + np.arange((~known).sum())   # unlabeled = singletons
        row = dict(variant=variant, subj=s, parts=int(lab.max()+1), E_found=E_blind(te_, Wh, lab),
                   E_null=E_blind(te_, Wh, lab[rng.permutation(94)]), E_eia=E_blind(te_, Wh, eia),
                   ARI_eia=ari(lab[known], MODLAB[known]),
                   ARI_hemi=ari(lab, HEMI),
                   ARI_sc=ari(lab, sclab),
                   groups={int(k): [b.LABELS[i] for i in np.flatnonzero(lab == k)] for k in np.unique(lab)})
        out.append(row)
        print(f"{variant:<6}{s:<8}{row['parts']:>7}{row['E_found']:>8.2f}{row['E_null']:>7.2f}{row['E_eia']:>10.2f}{row['ARI_eia']:>8.2f}{row['ARI_hemi']:>9.2f}{row['ARI_sc']:>7.2f}")
json.dump(out, open(b.HERE / "tick14_boundaries.json", "w"), indent=1)
