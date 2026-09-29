"""Tick 39: the subject-specific gap. Blocks from the FIRST half of a subject's own scan (lab1) gate the
model (with homotopic h=0.05); score against blocks from the SECOND half (lab2, never seen).
References: split-half reliability of empirical blocks (ARI lab1~lab2) and the empirical E_norm of lab1/lab2
on the second half. Compare with LOO-consensus gating."""
import numpy as np
import brain_eia as b
from tick14_boundaries import ari, louvain
from tick15_empirical import events, detect
from tick20_crossval import labels_of, sim, gate
from tick36_calibrated import infer_cond, E_norm
from tick38_homotopic import H

print(f"{'subj':<8}{'ARI l1~l2':>10}{'emp E(l1)':>10}{'emp E(l2)':>10} | {'model':<10}{'E(l1)':>7}{'E(l2)':>7}")
agg = {}
for s in b.SUBJECTS:
    C, tc = b.load(s); ev = events(tc); h1, h2 = ev[:len(ev)//2], ev[len(ev)//2:]
    lab1, _ = detect(h1, 39); lab2, _ = detect(h2, 40)
    Wemp = infer_cond(h1); rng = np.random.default_rng(39)
    e1, e2 = E_norm(h2, Wemp, lab1, rng), E_norm(h2, Wemp, lab2, rng)
    train = [x for x in b.SUBJECTS if x != s]
    co = sum((labels_of(x)[:, None] == labels_of(x)[None, :]).astype(float) for x in train) / 3
    np.fill_diagonal(co, 0); cons = louvain(co, 1.0, 21)
    agg.setdefault("emp", []).append((ari(lab1, lab2), e1, e2))
    print(f"{s:<8}{ari(lab1, lab2):>10.2f}{e1:>10.2f}{e2:>10.2f} |", end="")
    for name, blocks in [("own-h1", lab1), ("consensus", cons)]:
        r = []
        for seed in (81, 82):
            x = sim(gate(C + 0.05 * H, blocks), seed); mv = events(x); tr, te = mv[:len(mv)//2], mv[len(mv)//2:]
            Wm = infer_cond(tr); rg = np.random.default_rng(seed)
            r.append((E_norm(te, Wm, lab1, rg), E_norm(te, Wm, lab2, rg)))
        m = np.mean(r, 0); agg.setdefault(name, []).append(m)
        print(f" {name:<10}{m[0]:>7.2f}{m[1]:>7.2f}", end="")
    print(flush=True)
print("\nmeans:")
e = np.mean(agg["emp"], 0); print(f"  empirical: split-half ARI {e[0]:.2f}, E_norm(lab1) {e[1]:.2f}, E_norm(lab2) {e[2]:.2f}")
for k in ("own-h1", "consensus"):
    m = np.mean(agg[k], 0); print(f"  model gated by {k:<10}: E_norm(lab1) {m[0]:.2f}, E_norm(lab2 held-out) {m[1]:.2f}")
