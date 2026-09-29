"""Tick 78: how much intrinsic excitability must the DMN have to become a *specific* internal generator?
Drive-units on plain SC with the timescale hierarchy (tick 76); DMN units' alpha multiplied by f.
DMN-specific margin = (loop activity kept after silencing 16 strongest non-DMN) - (kept after silencing DMN).
2 subjects x 2 seeds, rate-matched."""
import numpy as np, scipy.sparse as sps
from tick47_units_on_sc import unit_matrix, R, N, te   # tick47 puts ../toy on sys.path
import brain_eia as b
from tick76_timescale_brain import reg, loop_units

def sim(W, rho, alpha, seed, T=3000, silent=None):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-rho)*d + alpha*u + inp + te.SIGMA*rng.standard_normal(N) - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float)
        if silent is not None: s[silent] = 0
        refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out[500:]

print(f"{'f (DMN alpha x)':>16}{'silence DMN':>12}{'silence top-16':>15}{'margin':>8}{'DMN share of activity':>23}")
dmn_units = np.isin(reg, b.IDX["DMN"])
for f in (1.0, 1.3, 1.6, 2.0):
    rows = []
    for s_ in b.SUBJECTS[:2]:
        C, _ = b.load(s_)
        pool = np.setdiff1d(np.arange(R), np.concatenate([b.IDX["DMN"], b.INIT_LOOP]))
        top = pool[np.argsort(C.sum(1)[pool])[-len(b.IDX["DMN"]):]]
        rho_reg = np.full(R, 0.12); rho_reg[np.concatenate([b.IDX["DMN"], b.IDX["VAL"]])] = 0.05; rho_reg[b.IDX["SEN"]] = 0.30
        rho = rho_reg[reg]; alpha = te.ALPHA * rho / te.RHO; alpha[dmn_units] *= f
        for seed in (1, 2):
            W1 = unit_matrix(C, seed); lo, hi = 0.3, 1.6
            for _ in range(9):
                mid = (lo+hi)/2; lo, hi = (mid, hi) if sim(sps.csr_matrix(W1*mid), rho, alpha, seed, 1500).mean() < 0.03 else (lo, mid)
            W = sps.csr_matrix(W1*(lo+hi)/2); intact = sim(W, rho, alpha, seed); base = intact[:, loop_units].mean()
            k = [sim(W, rho, alpha, seed, silent=np.isin(reg, g))[:, loop_units].mean() / base for g in (b.IDX["DMN"], top)]
            rows.append(k + [intact[:, dmn_units].sum() / intact.sum()])
    m = np.mean(rows, 0); print(f"{f:>16}{m[0]:>12.2f}{m[1]:>15.2f}{m[1]-m[0]:>+8.2f}{m[2]:>23.2f}", flush=True)
