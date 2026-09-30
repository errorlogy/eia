"""Tick 96: is B9 (degenerate empirical boundaries: split-half ARI 0.09) a detector artefact? Redo the split-half test on
all 7 subjects with the conditional-attribution graph for both detection and scoring (tick 36 method), vs the original
pairwise detector (tick 39)."""
import numpy as np, networkx as nx
import brain_eia as b
from tick14_boundaries import ari
from tick15_empirical import events, detect as detect_pairwise
from tick36_calibrated import infer_cond, E_norm
from tick81_initiators_7subj import SUBJ, load

def detect_cond(ev, seed):
    tr, te = ev[:len(ev)//2], ev[len(ev)//2:]; Wh = infer_cond(tr); rng = np.random.default_rng(seed); best = None
    G = nx.from_numpy_array(Wh + Wh.T)
    for res in [0.5, 0.8, 1, 1.5, 2, 3]:
        lab = np.empty(94, int)
        for k, c in enumerate(nx.community.louvain_communities(G, weight="weight", resolution=res, seed=seed)): lab[list(c)] = k
        sc = E_norm(te, Wh, lab, rng, n=5)
        if best is None or sc > best[0]: best = (sc, lab)
    return best[1]

if __name__ == "__main__":
    print(f"{'subject':<9}{'pairwise ARI':>13}{'conditional ARI':>16}{'E_norm(l1 on h2) cond':>23}{'#parts l1/l2':>14}")
    rows = []
    for s in SUBJ:
        _, tc = load(s); ev = events(tc); h1, h2 = ev[:len(ev)//2], ev[len(ev)//2:]
        p1, _ = detect_pairwise(h1, 39); p2, _ = detect_pairwise(h2, 40)
        c1, c2 = detect_cond(h1, 39), detect_cond(h2, 40)
        W = infer_cond(h1); e = E_norm(h2, W, c1, np.random.default_rng(1))
        rows.append((ari(p1, p2), ari(c1, c2), e))
        print(f"{s:<9}{rows[-1][0]:>13.2f}{rows[-1][1]:>16.2f}{e:>23.2f}{c1.max()+1:>8}/{c2.max()+1}", flush=True)
    m = np.mean(rows, 0); print(f"{'mean':<9}{m[0]:>13.2f}{m[1]:>16.2f}{m[2]:>23.2f}")
