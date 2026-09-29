"""Tick 17: can hemodynamics alone fake self-boundaries? Homogeneous Hopf model (no causal
blocks) -> canonical double-gamma HRF with block-specific latency and/or block-specific
measurement noise (blocks = empirical parts of 131217) -> same detector as tick 15.
If ARI with the blocks rises, empirical boundaries could be a hemodynamic/SNR artefact."""
import json
import numpy as np
from scipy.stats import gamma
import brain_eia as b
from tick14_boundaries import ari
from tick15_empirical import events, detect
from tick16_fit import C, G, w0, lab_emp, K

DT = 0.1
def neural(seed, T=1200 * b.TR + 40):
    rng = np.random.default_rng(seed); n = 94; om = 2*np.pi*w0; deg = C.sum(1); sq = np.sqrt(DT)*0.02
    z = 0.1*(rng.standard_normal(n)+1j*rng.standard_normal(n)); xs = []
    for _ in range(int(T/DT)):
        z = z + DT*((-0.02+1j*om)*z - np.abs(z)**2*z + G*(C@z-deg*z)) + sq*(rng.standard_normal(n)+1j*rng.standard_normal(n))
        xs.append(np.abs(z))                        # envelope as neural drive
    return np.array(xs).T

t = np.arange(0, 32, DT)
def hrf(shift):
    tt = np.clip(t - shift, 0, None)
    h = gamma.pdf(tt, 6) - gamma.pdf(tt, 16) / 6
    return h / h.sum()

def bold(x, lags, noise_mult, rng):
    out = np.empty_like(x)
    for i in range(94):
        out[i] = np.convolve(x[i] - x[i].mean(), hrf(lags[i]))[: x.shape[1]]
    out = out[:, int(40/DT)::int(round(b.TR/DT))][:, :1200]
    sd = out.std(1, keepdims=True)
    return out + rng.standard_normal(out.shape) * sd * 0.5 * noise_mult[:, None]

spread = np.linspace(0, 1, K)                       # block rank -> [0,1]
conds = {
    "common HRF":        (np.zeros(K), np.ones(K)),
    "lag spread 1 s":    (spread * 1.0, np.ones(K)),
    "lag spread 2 s":    (spread * 2.0, np.ones(K)),
    "SNR x1..x3":        (np.zeros(K), 1 + 2*spread),
    "lag 2 s + SNR":     (spread * 2.0, 1 + 2*spread),
}
res = {c: [] for c in conds}
for seed in [1, 2, 3]:
    x = neural(seed); rng = np.random.default_rng(seed + 50)
    for c, (lag_k, snr_k) in conds.items():
        lab, m = detect(events(bold(x, lag_k[lab_emp], snr_k[lab_emp], rng)), seed)
        res[c].append((ari(lab, lab_emp), m["E_found"] - m["E_null"]))
print(f"{'condition':<18}{'ARI vs blocks':>14}{'E gain':>8}")
for c, r in res.items():
    r = np.array(r); print(f"{c:<18}{r[:,0].mean():>9.2f}±{r[:,0].std():.2f}{r[:,1].mean():>8.2f}")
json.dump({c: np.array(r).tolist() for c, r in res.items()}, open(b.HERE / "tick17_hrf.json", "w"), indent=1)
