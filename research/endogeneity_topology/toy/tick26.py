"""Tick 26: do(Z) under lateral inhibition. SBM 10x100, mu=0.2, degree 5, rate-matched 0.03.
Conditions exc / cross_inh / dale20 (tick 25). u-only do(Z) on one module (tick 9), exact twin.
Metrics: early spread D_out (first 50 ticks), extra initiatives in target (z), spill-over (z). 10 seeds x 3 modules."""
import numpy as np, scipy.sparse as sps
import topo_endo as te
from tick25_lib import sbm, signed

N, T, T0 = 1000, 1600, 1000
def sim(W, seed, S=None, T=T):
    rng = np.random.default_rng(seed)
    d = rng.uniform(0, .3, N); u = rng.uniform(.2, .6, N); s = np.zeros(N); refr = np.zeros(N); out = np.zeros((T, N), bool)
    for t in range(T):
        if S is not None and t == T0: u[S] = 1.0
        xi = rng.standard_normal(N); inp = W @ s
        u = np.clip(u + te.AGE*(1-u) + te.BETA_U*inp*(1-u) - te.RESOLVE*u*s, 0, 1)
        d = np.clip((1-te.RHO)*d + te.ALPHA*u + inp + te.SIGMA*xi - .8*s, 0, 1)
        s = ((d > te.THETA) & (refr <= 0)).astype(float); refr = np.where(s > 0, 5, refr-1); out[t] = s > 0
    return out

if __name__ == "__main__":
    z = lambda x: x.mean() / (x.std(ddof=1)/np.sqrt(len(x)))
    print(f"{'condition':<11}{'D_out@50':>9}{'dI_in':>8}{'z_in':>7}{'dI_out':>9}{'z_out':>7}")
    for cond in ["exc", "cross_inh", "dale20"]:
        Do, a, b = [], [], []
        for seed in range(1, 11):
            A, truth = sbm(seed, 0.2); S1, _ = signed(A, truth, cond, seed)
            lo, hi = 0.5, 3.0
            for _ in range(11):
                m_ = (lo+hi)/2; lo, hi = (m_, hi) if sim(S1*m_, seed, T=1000)[500:].mean() < 0.03 else (lo, m_)
            W = sps.csr_matrix(S1*(lo+hi)/2); tw = sim(W, seed); p = tw[T0:].mean(); norm = 2*p*(1-p)
            for mod in range(3):
                ins = truth == mod; pe = sim(W, seed, np.flatnonzero(ins)); diff = pe[T0:] != tw[T0:]
                Do.append(diff[:50][:, ~ins].mean()/norm)
                a.append(int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum())); b.append(int(pe[T0:, ~ins].sum()) - int(tw[T0:, ~ins].sum()))
        a, b = np.array(a), np.array(b)
        print(f"{cond:<11}{np.mean(Do):>9.3f}{a.mean():>8.1f}{z(a):>7.2f}{b.mean():>9.1f}{z(b):>7.2f}", flush=True)
