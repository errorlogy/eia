"""Tick 103: region-level match between the connectome model's cascade-start share (tick 102) and empirical
self-initiation (tick 79) in the SAME subject, raw (no residualisation). Also partial correlation controlling for SC
strength (does the model predict empirical regional differences beyond strength?). 4 subjects."""
import numpy as np, scipy.sparse as sps
from scipy.stats import spearmanr, rankdata
import brain_eia as b
from tick47_units_on_sc import unit_matrix, R, N
from tick76_timescale_brain import sim, reg
from tick15_empirical import events
from tick36_calibrated import infer_cond, parents

def partial_spearman(x, y, z):
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz); ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    return np.corrcoef(ex, ey)[0, 1]

raw, part = [], []
for s_ in b.SUBJECTS:
    C, tc = b.load(s_); rho = np.full(N, 0.12); W1 = unit_matrix(C, 1); lo, hi = 0.5, 1.6
    for _ in range(9):
        mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(W1*mid), rho, 1, 1500).mean() < 0.03 else (lo, mid)
    W = sps.csr_matrix(W1*(lo+hi)/2); sp = sim(W, rho, 1)
    prev_in = np.vstack([np.zeros((1, N)), (sps.csr_matrix(sp[:-1].astype(float)) @ (W > 0).T.astype(float)).toarray()])
    model = np.array([(sp & (prev_in == 0))[:, reg == r].sum() / max(sp[:, reg == r].sum(), 1) for r in range(R)])
    ev = events(tc); tr, te = ev[:len(ev)//2], ev[len(ev)//2:]; tot = parents(te) @ infer_cond(tr).T
    emp = np.array([((tot[:, i] <= 1e-12) & te[:, i]).sum() / max(te[:, i].sum(), 1) for i in range(R)])
    raw.append(spearmanr(model, emp)[0]); part.append(partial_spearman(model, emp, C.sum(1)))
    print(f"{s_}: raw rho {raw[-1]:+.2f}   partial (| SC strength) {part[-1]:+.2f}", flush=True)
print(f"mean raw {np.mean(raw):+.2f}, mean partial {np.mean(part):+.2f}")
