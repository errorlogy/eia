"""Tick 2: width of the 'rich' regime vs gain (Griffiths-phase test), incl. hierarchical-modular."""
import numpy as np, networkx as nx
import topo_endo as te
te.T = 2000
N = te.N

def hier_mod(seed):
    sizes = [10]*20; P = np.zeros((20,20))
    for i in range(20):
        for j in range(20):
            P[i,j] = 0.35 if i==j else (0.03 if i//5==j//5 else 0.0015)
    return nx.stochastic_block_model(sizes, P.tolist(), seed=seed)

def topos(seed):
    t = te.topologies(seed)
    return {k: t[k] for k in ["ring_k4","small_world","erdos_renyi","scale_free","modular_sbm"]} | {"hier_modular": hier_mod(seed)}

gains = [0.7,0.8,0.9,1.0,1.1,1.2,1.3]
seeds = [1,2,3]
base = {}
res = {}
for sd in seeds:
    sp = te.simulate(np.zeros((N,N)), np.random.default_rng(sd)); base[sd] = sp[500:].mean()
    for name, g in topos(sd).items():
        for gn in gains:
            m = te.metrics(te.simulate(te.coupling(g, gn), np.random.default_rng(sd)), base[sd])
            res.setdefault((name,gn), []).append(m)
def rich(m): return m["rate_x_base"] > 1.5 and 0.7 <= m["cv_isi"] <= 2.5
print(f"{'topology':<14}" + "".join(f"{g:>7}" for g in gains) + "   width")
for name in ["ring_k4","small_world","erdos_renyi","scale_free","modular_sbm","hier_modular"]:
    cells, width = [], 0
    for gn in gains:
        ms = res[(name,gn)]
        frac = np.mean([rich(m) for m in ms])
        cv = np.nanmean([m["cv_isi"] for m in ms]); rx = np.mean([m["rate_x_base"] for m in ms])
        cells.append(f"{rx:4.1f}/{cv:.1f}{'*' if frac>=2/3 else ' '}")
        width += frac >= 2/3
    print(f"{name:<14}" + "".join(f"{c:>11}" for c in cells) + f"   {width}")
print("cell = rate_x_base / cv_isi ; * = rich in >=2/3 seeds")
