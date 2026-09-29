"""Tick 20: cross-subject validation. Blocks learned on 131217 (tick 15) gate the SC of the other
3 subjects (g_in 3, g_out 0.03). Targets: that subject's empirical FC and its own empirical
partition. Controls: no gate; gating with 3 shuffled block assignments (same sizes)."""
import json
import numpy as np
import brain_eia as b
from tick14_boundaries import ari
from tick15_empirical import events, detect
from tick16_fit import G, w0, lab_emp

emp = {r["subj"]: r for r in json.load(open(b.HERE / "tick15_empirical.json")) if r["src"] == "emp"}
idx = {l: i for i, l in enumerate(b.LABELS)}
def labels_of(s):
    lab = np.empty(94, int)
    for k, g in emp[s]["groups"].items(): lab[[idx[l] for l in g]] = int(k)
    return lab

def sim(Ce, seed, T=1200 * b.TR, dt=0.1):
    rng = np.random.default_rng(seed); n = 94; om = 2*np.pi*w0; deg = Ce.sum(1); sq = np.sqrt(dt)*0.02
    z = 0.1*(rng.standard_normal(n)+1j*rng.standard_normal(n)); xs = []; every = int(round(b.TR/dt))
    for t in range(int(T/dt)):
        z = z + dt*((-0.02+1j*om)*z - np.abs(z)**2*z + G*(Ce@z-deg*z)) + sq*(rng.standard_normal(n)+1j*rng.standard_normal(n))
        if t % every == 0: xs.append(z.real.copy())
    return np.array(xs).T

gate = lambda C, bl: C * np.where(bl[:, None] == bl[None, :], 3.0, 0.03)
if __name__ == "__main__":
    rng = np.random.default_rng(20)
    shuffles = [lab_emp[rng.permutation(94)] for _ in range(3)]
    rows = []
    print(f"{'subj':<8}{'condition':<16}{'FC fit':>7}{'ARI own emp':>12}{'E gain':>7}")
    for s in [x for x in b.SUBJECTS if x != "131217"]:
        C, tc = b.load(s); efc = b.fc(b.bandpass(tc)); own = labels_of(s)
        conds = [("no gate", C), ("131217 blocks", gate(C, lab_emp))] + [(f"shuffled {i}", gate(C, sh)) for i, sh in enumerate(shuffles)]
        for name, Ce in conds:
            r = []
            for seed in (41, 42):
                x = sim(Ce, seed); lab, m = detect(events(x), seed)
                r.append((np.corrcoef(efc, b.fc(b.bandpass(x)))[0, 1], ari(lab, own), m["E_found"] - m["E_null"]))
            r = np.mean(r, 0); rows.append(dict(subj=s, cond=name, fc=r[0], ari_own=r[1], e_gain=r[2]))
            print(f"{s:<8}{name:<16}{r[0]:>7.2f}{r[1]:>12.2f}{r[2]:>7.2f}")
    print("\nmeans over subjects:")
    for c in ["no gate", "131217 blocks", "shuffled"]:
        sel = [r for r in rows if r["cond"].startswith(c)]
        print(f"  {c:<16} FC {np.mean([r['fc'] for r in sel]):.2f}  ARI_own {np.mean([r['ari_own'] for r in sel]):.2f}  E gain {np.mean([r['e_gain'] for r in sel]):.2f}")
    json.dump(rows, open(b.HERE / "tick20_crossval.json", "w"), indent=1)
