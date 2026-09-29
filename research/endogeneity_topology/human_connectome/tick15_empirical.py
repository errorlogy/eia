"""Tick 15: blind self-boundary detector on EMPIRICAL rs-fMRI (HCP, 94 AAL2, 1200 TRs) vs the
Hopf model processed identically. Point-process events (Tagliazucchi 2012): upward crossings of
+1 SD of band-passed BOLD. Lags 1..3 TR. Train/test halves."""
import json, zlib
import numpy as np, networkx as nx
import brain_eia as b
from tick14_boundaries import ari, louvain, MODLAB, HEMI

LAGS = 3

def events(x):                      # x: (94, T)
    z = b.bandpass(x); z = (z - z.mean(1, keepdims=True)) / z.std(1, keepdims=True)
    up = z > 1.0
    return (up[:, 1:] & ~up[:, :-1]).T  # (T-1, 94)

def infer(ev):
    r = ev.mean(0); E = ev.astype(float); K = np.zeros((94, 94))
    for L in range(1, LAGS + 1):
        K += (E[:-L].T @ E[L:]).T - np.outer(r, r) * (len(ev) - L)
    np.fill_diagonal(K, 0); K = np.clip(K, 0, None)
    return np.where(K >= np.percentile(K[K > 0], 80), K, 0)

def E_blind(ev, Wh, lab):
    E = ev.astype(float); par = sum(np.vstack([np.zeros((L, 94)), E[:-L]]) for L in range(1, LAGS + 1))
    tot = par @ Wh.T; ins = par @ (Wh * (lab[:, None] == lab[None, :])).T
    return ((tot <= 1e-12) | (ins >= 0.5 * tot))[ev].mean()

def detect(ev, seed):
    rng = np.random.default_rng(seed); tr, te = ev[:len(ev)//2], ev[len(ev)//2:]
    Wh = infer(tr); best = None
    for res in [0.5, 0.8, 1, 1.5, 2, 3]:
        lab = louvain(Wh + Wh.T, res, seed)
        sc = E_blind(te, Wh, lab) - E_blind(te, Wh, lab[rng.permutation(94)])
        if best is None or sc > best[0]: best = (sc, lab)
    lab = best[1]
    eia = MODLAB.copy(); eia[MODLAB < 0] = 100 + np.arange((MODLAB < 0).sum())
    return lab, dict(parts=int(lab.max() + 1), E_found=E_blind(te, Wh, lab), E_null=E_blind(te, Wh, lab[rng.permutation(94)]),
                     E_eia=E_blind(te, Wh, eia), E_hemi=E_blind(te, Wh, HEMI))

G = json.loads(open(b.HERE / "results.json").read())["G_star"]
subj = {s: b.load(s) for s in b.SUBJECTS}
w = np.mean([b.peak_freqs(tc) for _, tc in subj.values()], axis=0)
known = MODLAB >= 0
labs = {"emp": {}, "model": {}}
print(f"{'source':<7}{'subj':<8}{'parts':>6}{'E_found':>8}{'E_null':>7}{'E_EIA':>7}{'E_hemi':>7}{'ARI_EIA':>8}{'ARI_hemi':>9}{'ARI_SC':>7}")
out = []
for s, (C, tc) in subj.items():
    seed = zlib.crc32(repr((s, 15)).encode())
    x_model, _ = b.simulate(C, w, G, np.random.default_rng(seed), T=1200 * b.TR)
    for src, x in [("emp", tc), ("model", x_model)]:
        lab, m = detect(events(x), seed); labs[src][s] = lab
        m.update(src=src, subj=s, ARI_eia=ari(lab[known], MODLAB[known]), ARI_hemi=ari(lab, HEMI), ARI_sc=ari(lab, louvain(C, 1.0, seed)),
                 groups={int(k): [b.LABELS[i] for i in np.flatnonzero(lab == k)] for k in np.unique(lab)})
        out.append(m)
        print(f"{src:<7}{s:<8}{m['parts']:>6}{m['E_found']:>8.2f}{m['E_null']:>7.2f}{m['E_eia']:>7.2f}{m['E_hemi']:>7.2f}{m['ARI_eia']:>8.2f}{m['ARI_hemi']:>9.2f}{m['ARI_sc']:>7.2f}")
for src in labs:
    ss = list(labs[src]); pa = [ari(labs[src][a], labs[src][c]) for i, a in enumerate(ss) for c in ss[i+1:]]
    print(f"cross-subject consistency ({src}): mean ARI {np.mean(pa):.2f}")
json.dump(out, open(b.HERE / "tick15_empirical.json", "w"), indent=1)
