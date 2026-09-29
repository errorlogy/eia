"""Tick 7: tick-6 do(Z) at rate-matched operating points (target rate 0.03)."""
import io, contextlib, runpy
import numpy as np, networkx as nx
from scipy.sparse.linalg import eigs
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path("tick6.py")
sim, build, N, T0 = ns["sim"], ns["build"], ns["N"], ns["T0"]
TARGET = 0.03

print(f"{'topology':<13}{'gain':>6}{'rate':>7}{'D_out@50':>10}{'D_out_end':>10}{'D_in_end':>10}{'dI_in':>8}{'z':>7}{'dI_out z':>9}")
for name in ["erdos_renyi", "modular_sbm", "hier_modular"]:
    Do50, Doe, Die, dIn, dOut, gains, rates = [], [], [], [], [], [], []
    for seed in [1, 2, 3]:
        g, mods, _ = build(name, seed)
        A = nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float)
        A1 = A / abs(eigs(A, k=1, which="LM", return_eigenvectors=False)[0])
        lo, hi = 0.8, 1.2
        for _ in range(10):
            mid = (lo + hi) / 2
            r = sim(A1 * mid, seed)[500:T0].mean()
            lo, hi = (mid, hi) if r < TARGET else (lo, mid)
        gain = (lo + hi) / 2; W = A1 * gain
        tw = sim(W, seed); p = tw[T0:].mean(); norm = 2*p*(1-p)
        gains.append(gain); rates.append(p)
        for S in mods:
            pe = sim(W, seed, S); diff = pe[T0:] != tw[T0:]
            ins = np.zeros(N, bool); ins[S] = True
            Do50.append(diff[:50][:, ~ins].mean()/norm); Doe.append(diff[-100:][:, ~ins].mean()/norm)
            Die.append(diff[-100:][:, ins].mean()/norm)
            dIn.append(int(pe[T0:, ins].sum()) - int(tw[T0:, ins].sum()))
            dOut.append(int(pe[T0:, ~ins].sum()) - int(tw[T0:, ~ins].sum()))
    dIn, dOut = np.array(dIn), np.array(dOut)
    z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
    print(f"{name:<13}{np.mean(gains):>6.3f}{np.mean(rates):>7.3f}{np.mean(Do50):>10.3f}{np.mean(Doe):>10.3f}{np.mean(Die):>10.3f}{dIn.mean():>8.1f}{z(dIn):>7.2f}{z(dOut):>9.2f}")
