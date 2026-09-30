"""Tick 146: does activity-bound routing (A38) on the human connectome shift self-boundaries from anatomy (hemispheres,
SC communities) to function (EIA map), as in real data (tick 36: hemispheres 0.05, EIA map 0.25, found 0.68)?
Drive-units on SC (94 x 10); co-activity gating beta in {0, 2}; rate-matched; E_norm (time-averaged gated W, true causes)
of unit partitions by hemisphere, SC-community and EIA map. 2 subjects x 1 seed."""
import sys
from pathlib import Path
import numpy as np, scipy.sparse as sps
import brain_eia as b
from tick14_boundaries import louvain, HEMI, MODLAB
from tick47_units_on_sc import unit_matrix, R, UPR, N, te
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "toy"))
reg = np.repeat(np.arange(R), UPR)

def sim(W, seed, beta, T):
    rng = np.random.default_rng(seed); Wc = W.tocoo(); r, c, w0 = Wc.row, Wc.col, Wc.data
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); tr = np.full(N, 0.03)
    out = np.zeros((T, N), bool); gs = np.zeros_like(w0)
    for t in range(T):
        if beta:
            z = (tr - tr.mean()) / (tr.std() + 1e-9); g = np.clip(1 + beta * (z[r] * z[c] - 1), 0, None); gs += g
            inp = np.bincount(r, weights=w0 * g * s[c], minlength=N)
        else:
            inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); tr += (s - tr) / 20; out[t] = s > 0
    return out[500:], sps.csr_matrix((w0 * (gs / T if beta else 1), (r, c)), shape=W.shape)

def E_norm(sp, W, lab, rng):
    P = sps.csr_matrix(sp[:-1].astype(float)); Sn = sp[1:]; Wc = W.tocoo(); tot = (P @ W.T).toarray()
    def E(l):
        k = l[Wc.row] == l[Wc.col]; Win = sps.csr_matrix((Wc.data[k], (Wc.row[k], Wc.col[k])), shape=W.shape)
        return ((tot <= 1e-12) | ((P @ Win.T).toarray() >= 0.5 * tot))[Sn].mean()
    en = np.mean([E(lab[rng.permutation(N)]) for _ in range(3)]); return (E(lab) - en) / (1 - en)

if __name__ == "__main__":
    eia = np.where(MODLAB >= 0, MODLAB, 100 + np.arange(R))
    print(f"{'beta':>5}{'hemispheres':>13}{'SC communities':>16}{'EIA map':>9}")
    for beta in (0.0, 2.0):
        rows = []
        for s_ in b.SUBJECTS[:2]:
            C, _ = b.load(s_); sc = louvain(C, 1.0, 146)
            W1 = sps.csr_matrix(unit_matrix(C, 1)); lo, hi = 0.3, 8.0
            for _ in range(10):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(W1*mid, 1, beta, 1500)[0].mean() < 0.03 else (lo, mid)
            sp, Wm = sim(W1*(lo+hi)/2, 1, beta, 4000); rng = np.random.default_rng(1)
            rows.append([E_norm(sp, Wm, lab[reg], rng) for lab in (HEMI, sc, eia)])
        m = np.mean(rows, 0); print(f"{beta:>5}{m[0]:>13.2f}{m[1]:>16.2f}{m[2]:>9.2f}", flush=True)
    print("empirical (tick 36): hemispheres 0.05, SC communities 0.24, EIA map 0.25")
