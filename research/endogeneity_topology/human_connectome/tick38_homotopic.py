"""Tick 38: does strengthening homotopic (L-R mirror) links dissolve the model's hemispheric boundary?
C_h = C + h * H (H = homotopic pairs; AAL2 order L,R adjacent). h in {0, .05, .1, .2} (max SC = 0.2).
With and without LOO-consensus gating. Calibrated E_norm + FC fit, held-out subject, 1 seed."""
import numpy as np
import brain_eia as b
from tick14_boundaries import louvain, MODLAB, HEMI
from tick15_empirical import events
from tick20_crossval import labels_of, sim, gate
from tick36_calibrated import infer_cond, E_norm

H = np.zeros((94, 94))
for k in range(47): H[2*k, 2*k+1] = H[2*k+1, 2*k] = 1
eia = MODLAB.copy(); eia[MODLAB < 0] = 100 + np.arange((MODLAB < 0).sum())
if __name__ == "__main__":
    hs = [0.0, 0.05, 0.1, 0.2]
    agg = {}
    for held in b.SUBJECTS:
        train = [s for s in b.SUBJECTS if s != held]
        co = sum((labels_of(s)[:, None] == labels_of(s)[None, :]).astype(float) for s in train) / 3
        np.fill_diagonal(co, 0); cons = louvain(co, 1.0, 21)
        C, tc = b.load(held); own = labels_of(held); efc = b.fc(b.bandpass(tc))
        for gated in (False, True):
            for h in hs:
                Ch = C + h * H; Ce = gate(Ch, cons) if gated else Ch
                x = sim(Ce, 71); ev = events(x); tr, te = ev[:len(ev)//2], ev[len(ev)//2:]
                Wh = infer_cond(tr); rng = np.random.default_rng(71)
                agg.setdefault((gated, h), []).append([E_norm(te, Wh, own, rng), E_norm(te, Wh, eia, rng), E_norm(te, Wh, HEMI, rng),
                                                       np.corrcoef(efc, b.fc(b.bandpass(x)))[0, 1]])
    print(f"{'gate':<6}{'h':>5}{'own':>7}{'EIA':>7}{'hemi':>7}{'FC fit':>8}")
    for (gated, h), rows in agg.items():
        m = np.mean(rows, 0); print(f"{'yes' if gated else 'no':<6}{h:>5.2f}" + "".join(f"{v:>7.2f}" for v in m[:3]) + f"{m[3]:>8.2f}")
    print("empirical reference: own 0.68, EIA 0.25, hemi 0.05")
