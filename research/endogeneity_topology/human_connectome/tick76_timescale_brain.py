"""Tick 76: does a timescale hierarchy make the DMN a specific internal generator on the human connectome?
Drive-units on SC (tick 47 model: 94 regions x 10 units). Homogeneous rho 0.12 vs hierarchy (DMN+VAL rho 0.05, SEN 0.30,
rest 0.12; alpha scaled with rho). Silencing = units clamped silent. Outcome: activity of the initiation loop
(SAL+BG+SMA units) relative to intact. Controls: silence the 16 strongest non-DMN non-loop regions; silence SEN.
Gain bisected to unit rate 0.03 per condition. 2 subjects x 2 seeds."""
import sys
from pathlib import Path
import numpy as np, scipy.sparse as sps
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "toy"))
import topo_endo as te
import brain_eia as b
from tick47_units_on_sc import unit_matrix, R, UPR, N

reg = np.repeat(np.arange(R), UPR)

def sim(W, rho, seed, T=3000, silent=None):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    alpha = te.ALPHA * rho / te.RHO
    for t in range(T):
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-rho)*d + alpha*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float)
        if silent is not None: s[silent] = 0
        refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out[500:]

loop_units = np.isin(reg, b.INIT_LOOP)
if __name__ == "__main__":
    print(f"{'condition':<13}{'silence DMN':>12}{'silence top-16':>15}{'silence SEN':>12}   (initiation-loop activity / intact)")
    for cond in ("homogeneous", "hierarchy"):
        rows = []
        for s_ in b.SUBJECTS[:2]:
            C, _ = b.load(s_)
            pool = np.setdiff1d(np.arange(R), np.concatenate([b.IDX["DMN"], b.INIT_LOOP]))
            top = pool[np.argsort(C.sum(1)[pool])[-len(b.IDX["DMN"]):]]
            rho_reg = np.full(R, 0.12)
            if cond == "hierarchy":
                rho_reg[np.concatenate([b.IDX["DMN"], b.IDX["VAL"]])] = 0.05; rho_reg[b.IDX["SEN"]] = 0.30
            rho = rho_reg[reg]
            for seed in (1, 2):
                W1 = unit_matrix(C, seed); lo, hi = 0.5, 1.6
                for _ in range(9):
                    mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(W1*mid), rho, seed, 1500).mean() < 0.03 else (lo, mid)
                W = sps.csr_matrix(W1*(lo+hi)/2)
                base = sim(W, rho, seed)[:, loop_units].mean()
                r = [sim(W, rho, seed, silent=np.isin(reg, grp))[:, loop_units].mean() / base
                     for grp in (b.IDX["DMN"], top, b.IDX["SEN"])]
                rows.append(r)
        m = np.mean(rows, 0); print(f"{cond:<13}{m[0]:>12.2f}{m[1]:>15.2f}{m[2]:>12.2f}", flush=True)
