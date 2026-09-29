"""Tick 36: re-score human self-boundaries with calibrated blind attribution (tick 35):
conditional regression attribution (lags 1..3 TR, top-10 candidates) + null-normalised
E_norm = (E(B) - E(rand)) / (1 - E(rand)), 20 size-matched permutations. Infer on first half, score second.
Partitions: empirical found (tick 15), EIA functional map, hemispheres, SC communities. Empirical vs model."""
import json, zlib
import numpy as np
import brain_eia as b
from tick14_boundaries import louvain, MODLAB, HEMI
from tick15_empirical import events

LAGS = 3

def parents(ev):
    E = ev.astype(float)
    return sum(np.vstack([np.zeros((L, 94)), E[:-L]]) for L in range(1, LAGS + 1))

def infer_cond(ev, cand=10):
    P = parents(ev); r = ev.mean(0); E = ev.astype(float)
    K = np.zeros((94, 94))
    for L in range(1, LAGS + 1):
        K += (E[:-L].T @ E[L:]).T - np.outer(r, r) * (len(ev) - L)
    np.fill_diagonal(K, 0); K = np.clip(K, 0, None)
    B = np.zeros((94, 94))
    for i in range(94):
        js = np.argsort(K[i])[-cand:]; js = js[K[i, js] > 0]
        if len(js) == 0: continue
        X = np.column_stack([np.ones(len(ev)), P[:, [i]], P[:, js]])
        B[i, js] = np.clip(np.linalg.lstsq(X, E[:, i], rcond=None)[0][2:], 0, None)
    thr = np.percentile(B[B > 0], 80) if (B > 0).any() else 0
    return np.where(B >= thr, B, 0)

def E(ev, Wh, lab):
    P = parents(ev); tot = P @ Wh.T; ins = P @ (Wh * (lab[:, None] == lab[None, :])).T
    return ((tot <= 1e-12) | (ins >= 0.5 * tot))[ev].mean()

def E_norm(ev, Wh, lab, rng, n=20):
    en = np.mean([E(ev, Wh, lab[rng.permutation(94)]) for _ in range(n)])
    return (E(ev, Wh, lab) - en) / (1 - en)

if __name__ == "__main__":
    G = json.loads(open(b.HERE / "results.json").read())["G_star"]
    emp15 = {r["subj"]: r for r in json.load(open(b.HERE / "tick15_empirical.json")) if r["src"] == "emp"}
    idx = {l: i for i, l in enumerate(b.LABELS)}
    subj = {s: b.load(s) for s in b.SUBJECTS}
    w = np.mean([b.peak_freqs(tc) for _, tc in subj.values()], axis=0)
    eia = MODLAB.copy(); eia[MODLAB < 0] = 100 + np.arange((MODLAB < 0).sum())
    print(f"{'source':<7}{'subj':<8}{'found(t15)':>11}{'EIA map':>9}{'hemi':>7}{'SC comm':>9}")
    agg = {"emp": [], "model": []}
    for s, (C, tc) in subj.items():
        found = np.empty(94, int)
        for k, g in emp15[s]["groups"].items(): found[[idx[l] for l in g]] = int(k)
        seed = zlib.crc32(repr((s, 36)).encode()); sc = louvain(C, 1.0, seed)
        x_model, _ = b.simulate(C, w, G, np.random.default_rng(seed), T=1200 * b.TR)
        for src, x in [("emp", tc), ("model", x_model)]:
            ev = events(x); tr, te = ev[:len(ev)//2], ev[len(ev)//2:]
            Wh = infer_cond(tr); rng = np.random.default_rng(seed)
            row = [E_norm(te, Wh, lab, rng) for lab in (found, eia, HEMI, sc)]
            agg[src].append(row)
            print(f"{src:<7}{s:<8}" + "".join(f"{v:>{w_}.2f}" for v, w_ in zip(row, (11, 9, 7, 9))))
    for src, rows in agg.items():
        m = np.mean(rows, 0); print(f"mean {src:<6}" + "".join(f"{v:>{w_}.2f}" for v, w_ in zip(m, (13, 9, 7, 9))))
