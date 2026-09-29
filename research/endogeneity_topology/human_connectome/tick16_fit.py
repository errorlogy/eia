"""Tick 16: which local-dynamics ingredient lets the Hopf model reproduce the empirical
self-boundaries? Subject 131217, blocks = empirical parts from tick 15.
Mechanisms (random search, 15 samples each):
  A  per-block bifurcation a_k in [-0.06, 0.02]
  W  per-block frequency offset d_k in [-8, 8] mHz (detuning)
Null for search bias: same search with block labels shuffled across regions.
Score = ARI(model partition, empirical partition); best candidate re-tested on a fresh seed."""
import json, zlib
import numpy as np
import brain_eia as b
from tick14_boundaries import ari
from tick15_empirical import events, detect

S = "131217"
G = json.loads(open(b.HERE / "results.json").read())["G_star"]
C, tc = b.load(S)
w0 = np.mean([b.peak_freqs(b.load(s)[1]) for s in b.SUBJECTS], axis=0)
emp = next(r for r in json.load(open(b.HERE / "tick15_empirical.json")) if r["src"] == "emp" and r["subj"] == S)
idx = {l: i for i, l in enumerate(b.LABELS)}
lab_emp = np.empty(94, int)
for k, g in emp["groups"].items(): lab_emp[[idx[l] for l in g]] = int(k)
K = lab_emp.max() + 1

def sim(a_vec, w, seed, T=1200 * b.TR, dt=0.1):
    rng = np.random.default_rng(seed); n = 94; om = 2*np.pi*w; deg = C.sum(1); sq = np.sqrt(dt)*0.02
    z = 0.1*(rng.standard_normal(n)+1j*rng.standard_normal(n)); xs = []; every = int(round(b.TR/dt))
    for t in range(int(T/dt)):
        z = z + dt*((a_vec+1j*om)*z - np.abs(z)**2*z + G*(C@z-deg*z)) + sq*(rng.standard_normal(n)+1j*rng.standard_normal(n))
        if t % every == 0: xs.append(z.real.copy())
    return np.array(xs).T

def score(a_vec, w, seed):
    lab, m = detect(events(sim(a_vec, w, seed)), seed)
    return ari(lab, lab_emp), m["E_found"] - m["E_null"]

if __name__ == "__main__":
    rng = np.random.default_rng(16)
    base = score(np.full(94, -0.02), w0, 1)
    print(f"baseline homogeneous: ARI {base[0]:.2f}, E gain {base[1]:.2f}")
    results = {}
    for mech in ["A", "W"]:
        for tag in ["true", "shuffled"]:
            blocks = lab_emp if tag == "true" else lab_emp[rng.permutation(94)]
            best = (-1, None)
            for i in range(15):
                p = rng.uniform(-0.06, 0.02, K) if mech == "A" else rng.uniform(-0.008, 0.008, K)
                a_vec = p[blocks] if mech == "A" else np.full(94, -0.02)
                w = w0 if mech == "A" else np.clip(w0 + p[blocks], 0.01, None)
                sc = score(a_vec, w, 100 + i)
                if sc[0] > best[0]: best = (sc[0], p, a_vec, w, sc[1])
            retest = score(best[2], best[3], 999)
            results[(mech, tag)] = dict(best_ARI=best[0], E_gain=best[4], retest_ARI=retest[0], retest_E_gain=retest[1], params=np.round(best[1], 4).tolist())
            print(f"{mech} {tag:<9} best ARI {best[0]:.2f} (E gain {best[4]:.2f}) | fresh-seed retest ARI {retest[0]:.2f} (E gain {retest[1]:.2f}) params {np.round(best[1], 4)}")
    json.dump({f"{k[0]}_{k[1]}": v for k, v in results.items()} | {"baseline": base, "empirical_E_gain": emp["E_found"] - emp["E_null"]},
              open(b.HERE / "tick16_fit.json", "w"), indent=1)
