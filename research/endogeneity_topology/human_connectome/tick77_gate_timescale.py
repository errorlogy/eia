"""Tick 77: can gating + timescale hierarchy make the DMN a *specific* internal generator (B1)?
Drive-units on SC; conditions: plain SC, gated+homotopic SC (LOO consensus), each with the timescale hierarchy.
Outcome as tick 76: initiation-loop activity after silencing DMN vs 16 strongest non-DMN regions vs sensory.
2 subjects x 2 seeds."""
import numpy as np, scipy.sparse as sps
import brain_eia as b
from tick14_boundaries import louvain
from tick20_crossval import labels_of, gate
from tick38_homotopic import H
from tick47_units_on_sc import unit_matrix, R
from tick76_timescale_brain import sim, reg, loop_units

print(f"{'SC':<16}{'silence DMN':>12}{'silence top-16':>15}{'silence SEN':>12}  DMN-specific margin")
for name in ("plain", "gated+homotopic"):
    rows = []
    for s_ in b.SUBJECTS[:2]:
        C, _ = b.load(s_)
        train = [x for x in b.SUBJECTS if x != s_]
        co = sum((labels_of(x)[:, None] == labels_of(x)[None, :]).astype(float) for x in train) / 3
        np.fill_diagonal(co, 0); cons = louvain(co, 1.0, 21)
        SC = C if name == "plain" else gate(C + 0.05 * H, cons)
        pool = np.setdiff1d(np.arange(R), np.concatenate([b.IDX["DMN"], b.INIT_LOOP]))
        top = pool[np.argsort(SC.sum(1)[pool])[-len(b.IDX["DMN"]):]]
        rho_reg = np.full(R, 0.12); rho_reg[np.concatenate([b.IDX["DMN"], b.IDX["VAL"]])] = 0.05; rho_reg[b.IDX["SEN"]] = 0.30
        rho = rho_reg[reg]
        for seed in (1, 2):
            W1 = unit_matrix(SC, seed); lo, hi = 0.5, 1.6
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(W1*mid), rho, seed, 1500).mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(W1*(lo+hi)/2); base = sim(W, rho, seed)[:, loop_units].mean()
            rows.append([sim(W, rho, seed, silent=np.isin(reg, g))[:, loop_units].mean() / base for g in (b.IDX["DMN"], top, b.IDX["SEN"])])
    m = np.mean(rows, 0); print(f"{name:<16}{m[0]:>12.2f}{m[1]:>15.2f}{m[2]:>12.2f}  {m[1]-m[0]:+.2f}", flush=True)
