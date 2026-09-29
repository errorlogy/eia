"""Tick 18: effective-connectivity gating. C_eff = C * (g_in if same block else g_out),
blocks = empirical parts of 131217. Grid g_in x g_out; null = shuffled blocks; best cell
re-tested on 2 fresh seeds."""
import json
import numpy as np
import brain_eia as b
from tick14_boundaries import ari
from tick15_empirical import events, detect
from tick16_fit import C, G, w0, lab_emp

def sim(Ce, seed, T=1200 * b.TR, dt=0.1):
    rng = np.random.default_rng(seed); n = 94; om = 2*np.pi*w0; deg = Ce.sum(1); sq = np.sqrt(dt)*0.02
    z = 0.1*(rng.standard_normal(n)+1j*rng.standard_normal(n)); xs = []; every = int(round(b.TR/dt))
    for t in range(int(T/dt)):
        z = z + dt*((-0.02+1j*om)*z - np.abs(z)**2*z + G*(Ce@z-deg*z)) + sq*(rng.standard_normal(n)+1j*rng.standard_normal(n))
        if t % every == 0: xs.append(z.real.copy())
    return np.array(xs).T

def run(blocks, gi, go, seed):
    same = blocks[:, None] == blocks[None, :]
    lab, m = detect(events(sim(C * np.where(same, gi, go), seed)), seed)
    return ari(lab, lab_emp), m["E_found"] - m["E_null"], ari(lab, blocks)

G_IN, G_OUT = [1, 2, 3], [1, 0.3, 0.1, 0.03]
rng = np.random.default_rng(18); shuf = lab_emp[rng.permutation(94)]
out = {}
for tag, blocks in [("true", lab_emp), ("shuffled", shuf)]:
    print(f"[{tag}] cells: ARI vs empirical / E gain / ARI vs imposed blocks")
    grid = {}
    for gi in G_IN:
        row = []
        for go in G_OUT:
            r = run(blocks, gi, go, 7); grid[(gi, go)] = r
            row.append(f"{r[0]:5.2f}/{r[1]:.2f}/{r[2]:.2f}")
        print(f"  g_in={gi:<3}" + "  ".join(row) + f"   (g_out={G_OUT})")
    best = max(grid, key=lambda k: grid[k][2])
    rt = [run(blocks, *best, s) for s in (101, 202)]
    out[tag] = dict(grid={f"{k[0]}_{k[1]}": v for k, v in grid.items()}, best=best, retest=rt)
    print(f"  best (by imposed-block ARI) g_in={best[0]} g_out={best[1]} -> retest ARI_emp {[round(x[0],2) for x in rt]}, E gain {[round(x[1],2) for x in rt]}, ARI_blocks {[round(x[2],2) for x in rt]}")
json.dump(out, open(b.HERE / "tick18_gating.json", "w"), indent=1, default=list)
