# Run from a repo copy with patches/combined_all.patch applied (uses causal_audit=True).
"""PAI-EI-E0-001 baseline matrix with lexical vs causal (D1) structural gate — run on a patched COPY of the repo."""
import sys
from pathlib import Path
sys.path.insert(0, "src")
from eia.experiment.baseline import BaselineCondition
from eia.pipeline import run_scenario
import runpy
ns = runpy.run_path("research/run_pai_ei_e0_001_full_matrix.py", run_name="not_main")
BASELINES, SCEN = ns["BASELINES"], ns.get("SCENARIOS")
if SCEN is None:
    SCEN = [Path("scenarios/twin_world_001.yaml")] + sorted(Path("evals").glob("twin_world_*.yaml"))
print(f"{'baseline':<20}{'endogenous (lexical)':>21}{'endogenous (causal)':>21}{'origins (causal)':>40}")
for bl in BASELINES:
    lex = cau = 0; origins = {}
    for sp in SCEN:
        seed = 100
        a = run_scenario(Path(sp), traces_dir=Path("_tr"), seed=seed, baseline=BaselineCondition(bl))
        c = run_scenario(Path(sp), traces_dir=Path("_tr"), seed=seed, baseline=BaselineCondition(bl), causal_audit=True)
        lex += a["authentic_verdict"].initiative_class == "endogenous"; cau += c["authentic_verdict"].initiative_class == "endogenous"
        o = (c["drive_attribution"] or {}).get("origin", "none(abstain/stub)"); origins[o] = origins.get(o, 0) + 1
    print(f"{bl:<20}{lex:>14}/{len(SCEN)}{cau:>14}/{len(SCEN)}{str(origins):>40}", flush=True)
