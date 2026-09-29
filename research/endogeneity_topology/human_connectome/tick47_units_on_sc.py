"""Tick 47: test toy A2 (modular structure smooths the silence->seizure transition) on the HUMAN
connectome with additive excitatory drive-units (topo_endo dynamics) instead of diffusive Hopf.
Each of 94 regions = 10 units (within-region p=0.5); between-region coupling = SC weights.
SC variants: plain, gated+homotopic (LOO consensus, g_in 3, g_out 0.03, h 0.05), degree-preserving rewired.
Gain (spectral-radius normalised) sweep; max step jump of rate x base, rich width. 2 subjects x 2 seeds."""
import sys
from pathlib import Path
import numpy as np, scipy.sparse as sps
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "toy"))
import topo_endo as te
import brain_eia as b
from tick14_boundaries import louvain
from tick20_crossval import labels_of, gate
from tick38_homotopic import H

R, UPR = 94, 10
N = R * UPR
te.N = N

def unit_matrix(SC, seed):
    rng = np.random.default_rng(seed); reg = np.repeat(np.arange(R), UPR)
    within = (reg[:, None] == reg[None, :]) & (rng.random((N, N)) < 0.5); np.fill_diagonal(within, False)
    between = SC[reg][:, reg] / SC.max() * (rng.random((N, N)) < 0.5)
    W = within * 0.2 + between * (reg[:, None] != reg[None, :])
    W = (W + W.T) / 2
    return W / np.max(np.abs(np.linalg.eigvalsh(W)))

gains = [round(0.80 + 0.05*i, 2) for i in range(11)]
res = {}
for s in b.SUBJECTS[:2]:
    train = [x for x in b.SUBJECTS if x != s]
    co = sum((labels_of(x)[:, None] == labels_of(x)[None, :]).astype(float) for x in train) / 3
    np.fill_diagonal(co, 0); cons = louvain(co, 1.0, 21)
    C, _ = b.load(s)
    variants = {"plain SC": C, "gated+homotopic": gate(C + 0.05*H, cons), "rewired SC": b.rewire(C, np.random.default_rng(47))}
    for name, SC in variants.items():
        for seed in (1, 2):
            W1 = unit_matrix(SC, seed)
            b0 = te.simulate(sps.csr_matrix((N, N)), np.random.default_rng(seed))[500:].mean()
            rates = [te.simulate(sps.csr_matrix(W1 * g), np.random.default_rng(seed))[500:].mean() / b0 for g in gains]
            res.setdefault(name, []).append(rates)
print("gain:            " + " ".join(f"{g:>5}" for g in gains))
for name, rows in res.items():
    r = np.mean(rows, 0); jump = np.max(np.diff(r))
    print(f"{name:<16} " + " ".join(f"{x:>5.1f}" for x in r) + f"   max jump {jump:.1f}")
