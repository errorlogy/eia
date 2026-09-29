"""Tick 19: FC fit under gating, and constant vs intermittent (state-dependent) gate.
Intermittent gate: telegraph process, mean dwell 20 s, ON fraction f; ON = (g_in 3, g_out 0.03),
OFF = plain SC. Subject 131217. Metrics: ARI vs empirical partition, E gain, FC fit."""
import json
import numpy as np
import brain_eia as b
from tick14_boundaries import ari
from tick15_empirical import events, detect
from tick16_fit import C, G, w0, lab_emp, tc

same = lab_emp[:, None] == lab_emp[None, :]
C_on = C * np.where(same, 3.0, 0.03)
emp_fc = b.fc(b.bandpass(tc))

def sim(seed, frac_on, C_const=None, T=1200 * b.TR, dt=0.1, dwell=20.0):
    rng = np.random.default_rng(seed); n = 94; om = 2*np.pi*w0; sq = np.sqrt(dt)*0.02
    z = 0.1*(rng.standard_normal(n)+1j*rng.standard_normal(n)); xs = []; every = int(round(b.TR/dt))
    on = rng.random() < frac_on; t_on = 0
    for t in range(int(T/dt)):
        if C_const is None:
            rate = 1/(dwell*frac_on) if on else 1/(dwell*(1-frac_on)) if frac_on < 1 else 0
            if rng.random() < rate*dt: on = not on
            Ce = C_on if on else C; t_on += on
        else:
            Ce = C_const
        z = z + dt*((-0.02+1j*om)*z - np.abs(z)**2*z + G*(Ce@z-Ce.sum(1)*z)) + sq*(rng.standard_normal(n)+1j*rng.standard_normal(n))
        if t % every == 0: xs.append(z.real.copy())
    return np.array(xs).T, t_on / int(T/dt)

conds = {"no gate": (None, C), "constant (2, 0.1)": (None, C*np.where(same, 2.0, 0.1)), "constant (3, 0.03)": (None, C_on),
         "intermittent 25%": (0.25, None), "intermittent 50%": (0.5, None), "intermittent 75%": (0.75, None)}
print(f"{'condition':<20}{'ON time':>8}{'ARI_emp':>8}{'E gain':>7}{'FC fit':>7}")
out = {}
for name, (f, Cc) in conds.items():
    rs = []
    for seed in (31, 32):
        x, ton = sim(seed, f if f is not None else 1.0, Cc)
        lab, m = detect(events(x), seed)
        rs.append((ton if f is not None else float(Cc is C_on), ari(lab, lab_emp), m["E_found"]-m["E_null"], np.corrcoef(emp_fc, b.fc(b.bandpass(x)))[0, 1]))
    r = np.mean(rs, 0); out[name] = np.array(rs).tolist()
    print(f"{name:<20}{r[0] if f is not None else float('nan'):>8.2f}{r[1]:>8.2f}{r[2]:>7.2f}{r[3]:>7.2f}")
json.dump(out, open(b.HERE / "tick19_gate_state.json", "w"), indent=1)
