"""Silent-run probe of PopulationDrives: is irregular initiative intrinsic dynamics or noise?
Eligible tick = max drive intensity >= 0.30 (IntentionGenesis abstain_threshold). Fixed BeliefField tension, no observations."""
import numpy as np
from eia.drives.population import PopulationDrives, PopulationParams
from eia.beliefs import BeliefField

class FixedField(BeliefField):
    pass

class _F:
    def __init__(self, t): self.t = t; self.contradictions = []; self.beliefs = {}; self.updates = []
    def gradient_snapshot(self): return {"epistemic": self.t, "coherence": self.t, "commitment": self.t}
    def highest_entropy_beliefs(self, n): return []
def field_with(t): return _F(t)

def run(tension, sigma, seed, ticks=400):
    e = PopulationDrives(PopulationParams(seed=seed, sigma=sigma))
    f = field_with(tension)
    elig = []
    for i in range(ticks):
        m = e.compute(f, motivation_id=f"m{i}")
        elig.append(max(s.intensity for s in m.signals) >= 0.30)
    x = np.array(elig[50:])  # drop transient
    idx = np.flatnonzero(x)
    isi = np.diff(idx)
    cv = isi.std() / isi.mean() if len(isi) > 2 else np.nan
    # serial dependence of ISIs (Poisson/renewal null ≈ 0)
    r1 = np.corrcoef(isi[:-1], isi[1:])[0, 1] if len(isi) > 5 else np.nan
    # Fano factor of counts in 20-tick windows (Poisson ≈ 1)
    w = x[: len(x) // 20 * 20].reshape(-1, 20).sum(1); fano = w.var() / w.mean() if w.mean() > 0 else np.nan
    return x.mean(), cv, r1, fano

print(f"{'tension':>7} {'sigma':>6} | {'rate':>6} {'ISI CV':>7} {'ISI r1':>7} {'Fano':>6}   (mean over 5 seeds)")
for t in (0.0, 0.2, 0.4, 0.6, 0.8):
    for sg in (0.03, 0.0):
        rs = np.array([run(t, sg, s) for s in range(5)])
        m = np.nanmean(rs, 0)
        print(f"{t:>7.1f} {sg:>6.2f} | {m[0]:>6.3f} {m[1]:>7.2f} {m[2]:>7.2f} {m[3]:>6.2f}")
