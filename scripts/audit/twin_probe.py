"""Probe: does the twin actually lack the removed user events?"""
import glob, tempfile
from pathlib import Path
from eia.pipeline import run_scenario, CognitiveLoop
from eia.schemas.belief import BeliefKind
from eia.simulator import load_scenario

for sp in sorted(glob.glob("evals/twin_world_*.yaml")) + ["scenarios/twin_world_001.yaml"]:
    r = run_scenario(Path(sp), traces_dir=Path(tempfile.mkdtemp()))
    loop, sim = r["loop"], r["simulator"]
    removed = set(r["twin_result"].removed_user_event_ids)
    snap = loop._snapshot_field
    # beliefs touched by removed events are still present in the twin's field?
    upd_from_removed = [u for u in snap.updates if getattr(u, "source_observation_id", None) in removed or any(rid in str(u.model_dump()) for rid in removed)]
    # honest twin: rebuild field from scenario, replaying all observations EXCEPT removed ones
    sc = load_scenario(Path(sp))
    hl = CognitiveLoop(seed=sc.seed)
    for spec in sc.initial_beliefs:
        hl.field.upsert_belief(spec["id"], kind=BeliefKind(spec.get("kind","categorical")), subject=spec["subject"], claim=spec["claim"], distribution=spec.get("distribution"), uncertainty=spec.get("uncertainty",0.5), metadata=spec.get("metadata",{}))
    for c in sc.metadata.get("contradictions", []):
        hl.field.register_contradiction(c[0], c[1], c[2])
    kept = [o for o in sim.bus.events if o.id not in removed]
    # note: bus.events after policy — check whether removed are still in bus
    for o in r["simulator"].bus.events:
        pass
    for o in kept: hl.apply_observation(o)
    from eia.pipeline import CognitiveLoop as CL
    ticks = 3
    for i in range(ticks):
        m, ini, d, _ = hl.tick_cognition(tick=sim.clock.tick+i, hour=sim.clock.hour, finalize=(i==ticks-1))
    honest_eoi = loop.twin_runner.compare(r["initiative"], ini, list(removed)).eoi
    print(f"{Path(sp).stem:18s} removed={len(removed)} traces_of_removed_in_twin_field={len(upd_from_removed)} "
          f"reported_EOI={r['twin_result'].eoi:.2f} honest_twin_EOI={honest_eoi:.2f} "
          f"orig={r['initiative'].candidate.kind.value}/{r['initiative'].candidate.target_belief_id} "
          f"honest_twin={ini.candidate.kind.value}/{ini.candidate.target_belief_id}")
