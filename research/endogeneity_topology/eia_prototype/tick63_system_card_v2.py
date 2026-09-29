"""Tick 63: system card v2 — tick 57 with the calibrated engine (tick 60 targets + tick 62 subcritical gain 0.4,
burst_frac 0.15). Same metrics, 7 scenarios x 3 seeds."""
import numpy as np
import tick30_pipeline as h
import tick57_system_card as t57
from population_drives import PopulationParams
from tick60_target_uncertainty import TargetAdapter, TargetEngine

TargetEngine.aging_k = 0.05
_orig_use = h.use_population

def use_population(on):
    _orig_use(on)
    if on:
        h.pl.DriveEngine = TargetAdapter
h.use_population = use_population
_PP = PopulationParams

class Params(_PP):
    def __init__(self, seed=0, mu=0.05, ext_gain=0.02, **kw):
        super().__init__(seed=seed, mu=mu, alpha=0.2, gain=0.4, burst_frac=0.15)
t57.PopulationParams = Params
h.PopDriveAdapter.params = Params()

if __name__ == "__main__":
    import runpy, sys
    sys.argv = ["tick57"]
    agg = {"current": [], "proposed": []}
    print(f"{'scenario':<21}{'system':<10}{'1st same':>9}{'EOI':>6}{'v(all)':>8}{'asks/200':>9}{'max run':>8}{'ISI CV':>8}")
    for sp in h.SCENARIOS:
        ref = None
        for system in ("current", "proposed"):
            if system == "proposed":
                TargetAdapter.params = Params(seed=1)
            rs = []
            for s in (1, 2, 3):
                if system == "proposed":
                    TargetAdapter.params = Params(seed=s)
                rs.append(t57.card(sp, system, s))
            if system == "current":
                ref = rs[0]["first"]
            m = dict(same=np.mean([x["first"] == ref for x in rs]), eoi=np.mean([x["eoi"] for x in rs]), vall=np.mean([x["vall"] for x in rs]),
                     asks=np.mean([x["asks"] for x in rs]), max_run=np.mean([x["max_run"] for x in rs]), cv=np.nanmean([x["cv"] for x in rs]))
            agg[system].append(m)
            print(f"{sp.stem:<21}{system:<10}{m['same']:>9.2f}{m['eoi']:>6.2f}{m['vall']:>8.2f}{m['asks']:>9.1f}{m['max_run']:>8.1f}{m['cv']:>8.2f}", flush=True)
    print("\nmeans:")
    for system, rows in agg.items():
        print(f"  {system:<9}" + "  ".join(f"{k} {np.nanmean([r[k] for r in rows]):.2f}" for k in rows[0]))
