"""Tick 29: PopulationDriveEngine vs eia DriveEngine at X_trigger = 0.
(1) silence dynamics: intensity trajectories with a static belief field
(2) initiative timing: events per drive, ISI CV
(3) motive separability / controllability: boost a non-dominant drive, effect on it vs others,
    for mu 0.05 excitatory, mu 0.3 excitatory, mu 0.3 lateral inhibition. 10 seeds."""

import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from eia.beliefs import BeliefField  # noqa: E402
from eia.drives import DriveEngine  # noqa: E402
from eia.schemas.belief import Belief, BeliefKind  # noqa: E402
from eia.schemas.motivation import DriveKind  # noqa: E402
from population_drives import DRIVES, PopulationDriveEngine, PopulationParams  # noqa: E402


def field_with(u: float) -> BeliefField:
    now = datetime.now(timezone.utc)
    f = BeliefField()
    f.add_belief(Belief(id="b1", kind=BeliefKind.CATEGORICAL, subject="s", claim="c",
                        distribution={"a": 1 - u, "b": u}, created_at=now, updated_at=now))
    return f


def silence(eng_factory, u, ticks=400):
    f = field_with(u); eng = eng_factory(); tr = []
    for _ in range(ticks):
        m = eng.compute(f); tr.append([s.intensity for s in m.signals])
    return np.array(tr)


print("(1) silence, epistemic intensity at ticks 10/50/200/400 and std over ticks 100-400")
for u in (0.05, 0.5):
    base = silence(DriveEngine, u)[:, 0]
    pop = silence(lambda: PopulationDriveEngine(PopulationParams(seed=1)), u)[:, 0]
    print(f"  belief u={u}: DriveEngine {base[[9, 49, 199, 399]].round(3)} sd {base[100:].std():.3f} | "
          f"Population {pop[[9, 49, 199, 399]].round(3)} sd {pop[100:].std():.3f}")

print("\n(2) initiative events over 3000 silent ticks (no beliefs)")
eng = PopulationDriveEngine(PopulationParams(seed=2)); ev = {k: [] for k in DRIVES}
for t in range(3000):
    for k in eng.initiatives(eng.step()):
        ev[k].append(t)
for k, ts in ev.items():
    isi = np.diff(ts)
    print(f"  {k.value:<11} events {len(ts):>4}  ISI CV {isi.std()/isi.mean() if len(isi) > 2 else float('nan'):.2f}")


def boost_effect(params, seed, t0=1500, horizon=400):
    effects = []
    for k in DRIVES:
        runs = []
        for do in (False, True):
            eng = PopulationDriveEngine(PopulationParams(**{**params, "seed": seed}))
            eng.rng = np.random.default_rng(seed + 999)
            hist = []
            for t in range(t0 + horizon):
                hist.append(eng.step(boost={k: 1.0} if (do and t == t0) else None))
            runs.append(np.array(hist))
        base, pert = runs
        dom = int(np.argmax(base[t0 - 50:t0].sum(0)))
        if DRIVES.index(k) == dom:
            continue                      # tick 28: boost only non-dominant motives
        i = DRIVES.index(k)
        d_self = (pert[t0:, i] - base[t0:, i]).sum() * params.get("units", 60)
        d_rest = (np.delete(pert[t0:], i, 1) - np.delete(base[t0:], i, 1)).sum() * params.get("units", 60)
        effects.append((d_self, d_rest))
    return effects


print("\n(3) boost u=1 of a non-dominant drive (10 seeds); delta unit-initiatives over 400 ticks")
for name, prm in [("mu 0.05 exc", dict(mu=0.05)), ("mu 0.30 exc", dict(mu=0.30)), ("mu 0.30 lat-inh", dict(mu=0.30, cross_inhibitory=True))]:
    eff = np.array([e for s in range(1, 11) for e in boost_effect(prm, s)])
    z = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
    print(f"  {name:<16} n={len(eff):>2}  self {eff[:,0].mean():>7.1f} (z {z(eff[:,0]):5.2f})  rest {eff[:,1].mean():>7.1f} (z {z(eff[:,1]):5.2f})")
