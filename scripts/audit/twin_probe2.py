import glob, tempfile
from pathlib import Path
from eia.pipeline import run_scenario, CognitiveLoop
from eia.schemas.belief import BeliefKind
from eia.simulator import load_scenario, Simulator

def honest(sp, keep):
    sc = load_scenario(Path(sp)); sim = Simulator(sc, seed=sc.seed)
    sim.run_until(max((e.tick for e in sc.events), default=10))
    obs = [o for o in sim.bus.events if keep(o)]
    hl = CognitiveLoop(seed=sc.seed)
    for s in sc.initial_beliefs:
        hl.field.upsert_belief(s["id"], kind=BeliefKind(s.get("kind","categorical")), subject=s["subject"], claim=s["claim"], distribution=s.get("distribution"), uncertainty=s.get("uncertainty",0.5), metadata=s.get("metadata",{}))
    for c in sc.metadata.get("contradictions", []): hl.field.register_contradiction(*c)
    for o in obs: hl.apply_observation(o)
    sim.advance_quiet_period(ticks=4)
    for i in range(3):
        m, ini, d, _ = hl.tick_cognition(tick=sim.clock.tick+i, hour=sim.clock.hour, finalize=(i==2))
    return ini, d, len(sim.bus.events), len(obs)

for sp in sorted(glob.glob("evals/twin_world_*.yaml")) + ["scenarios/twin_world_001.yaml"]:
    r = run_scenario(Path(sp), traces_dir=Path(tempfile.mkdtemp()))
    o = r["initiative"]
    a, _, n, k = honest(sp, lambda ob: not getattr(ob, "is_user_trigger", False) and "user" not in str(getattr(ob,"source","")))
    b, db, _, _ = honest(sp, lambda ob: False)
    sc = r["loop"].twin_runner
    print(f"{Path(sp).stem}: events={n} | no-user({k} kept): {a.candidate.kind.value}/{a.candidate.target_belief_id} EOI={sc.compare(o,a,['x']).eoi:.2f} "
          f"| NO observations at all: {b.candidate.kind.value}/{b.candidate.target_belief_id} gov={db.outcome.value} EOI={sc.compare(o,b,['x']).eoi:.2f}")
