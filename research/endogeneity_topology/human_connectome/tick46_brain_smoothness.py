"""Tick 46: toy A2 (modularity smooths the silence->activity transition) in the human model.
Sweep global coupling G; mean envelope (activity) and burstiness (CV of the initiation-loop drive D)
for plain SC vs gated + homotopic SC (LOO consensus). Max normalised slope of activity vs G."""
import numpy as np
import brain_eia as b
from tick14_boundaries import louvain
from tick16_fit import w0
from tick20_crossval import labels_of, gate
from tick38_homotopic import H

def sim(Ce, Gv, seed, T=300.0, dt=0.1):
    rng = np.random.default_rng(seed); n = 94; om = 2*np.pi*w0; deg = Ce.sum(1); sq = np.sqrt(dt)*0.02
    z = 0.1*(rng.standard_normal(n)+1j*rng.standard_normal(n)); env = []
    for t in range(int(T/dt)):
        z = z + dt*((-0.02+1j*om)*z - np.abs(z)**2*z + Gv*(Ce@z-deg*z)) + sq*(rng.standard_normal(n)+1j*rng.standard_normal(n))
        if t % 5 == 0 and t*dt > 60: env.append(np.abs(z))
    return np.array(env)

Gs = [0.2, 0.4, 0.6, 0.8, 1.0, 1.3, 1.6, 2.0, 2.5, 3.0]
res = {}
for s in b.SUBJECTS:
    train = [x for x in b.SUBJECTS if x != s]
    co = sum((labels_of(x)[:, None] == labels_of(x)[None, :]).astype(float) for x in train) / 3
    np.fill_diagonal(co, 0); cons = louvain(co, 1.0, 21)
    C, _ = b.load(s)
    for name, Ce in [("plain SC", C), ("gated+homotopic", gate(C + 0.05*H, cons))]:
        act, cv = [], []
        for Gv in Gs:
            e = sim(Ce, Gv, 3); D = e[:, b.INIT_LOOP].mean(1)
            act.append(e.mean()); cv.append(D.std() / D.mean())
        res.setdefault(name, []).append((act, cv))
print("G:              " + " ".join(f"{g:>6}" for g in Gs))
for name, rows in res.items():
    a = np.mean([r[0] for r in rows], 0); c = np.mean([r[1] for r in rows], 0)
    slope = np.max(np.abs(np.diff(a) / np.diff(Gs))) / (a.max() - a.min() + 1e-12)
    print(f"{name:<16}" + " ".join(f"{x:>6.3f}" for x in a) + f"   activity; max norm. slope {slope:.2f}")
    print(f"{'':<16}" + " ".join(f"{x:>6.3f}" for x in c) + "   CV of initiation drive")
