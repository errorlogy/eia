"""Tick 21: leave-one-subject-out. Consensus blocks from the other 3 subjects' empirical partitions
(co-assignment matrix -> Louvain) gate (3, 0.03) the held-out subject's SC. Scored against the
held-out subject's own empirical partition, E gain, FC. Controls: no gate, 2 shuffled consensus."""
import json
import numpy as np
import brain_eia as b
from tick14_boundaries import ari, louvain
from tick15_empirical import events, detect
from tick20_crossval import labels_of, sim, gate

rows = []
print(f"{'held-out':<9}{'#blocks':>8}{'ARI cons~own':>13} | {'cond':<11}{'FC':>6}{'ARI own':>8}{'E gain':>7}")
for held in b.SUBJECTS:
    train = [s for s in b.SUBJECTS if s != held]
    co = sum((labels_of(s)[:, None] == labels_of(s)[None, :]).astype(float) for s in train) / len(train)
    np.fill_diagonal(co, 0)
    cons = louvain(co, 1.0, 21)
    own = labels_of(held); C, tc = b.load(held); efc = b.fc(b.bandpass(tc))
    rng = np.random.default_rng(21)
    conds = [("no gate", C), ("consensus", gate(C, cons))] + [(f"shuffled{i}", gate(C, cons[rng.permutation(94)])) for i in range(2)]
    for name, Ce in conds:
        r = []
        for seed in (51, 52):
            x = sim(Ce, seed); lab, m = detect(events(x), seed)
            r.append((np.corrcoef(efc, b.fc(b.bandpass(x)))[0, 1], ari(lab, own), m["E_found"] - m["E_null"]))
        r = np.mean(r, 0); rows.append(dict(held=held, cond=name, fc=r[0], ari_own=r[1], e_gain=r[2], n_blocks=int(cons.max()+1)))
        print(f"{held:<9}{cons.max()+1:>8}{ari(cons, own):>13.2f} | {name:<11}{r[0]:>6.2f}{r[1]:>8.2f}{r[2]:>7.2f}")
print("\nmeans over held-out subjects:")
for c in ["no gate", "consensus", "shuffled"]:
    sel = [r for r in rows if r["cond"].startswith(c)]
    print(f"  {c:<10} FC {np.mean([r['fc'] for r in sel]):.2f}  ARI_own {np.mean([r['ari_own'] for r in sel]):.2f}  E gain {np.mean([r['e_gain'] for r in sel]):.2f}")
json.dump(rows, open(b.HERE / "tick21_loo.json", "w"), indent=1)
