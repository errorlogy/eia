"""Control matrix for EIA initiative: which inputs is the initiative actually sensitive to?
Usage: PYTHONPATH=<src> python controls.py <repo_root> <engine> <seeds...>"""
import copy
import sys
import tempfile
import glob
import json
import collections
import inspect
import io
import contextlib
from pathlib import Path
import yaml
from eia.pipeline import run_scenario

root, engine, seeds = Path(sys.argv[1]), sys.argv[2], [int(s) for s in sys.argv[3:]] or [None]
paths = sorted(glob.glob(str(root / "evals/twin_world_*.yaml"))) + [str(root / "scenarios/twin_world_001.yaml")]
kw = {"drive_engine": engine} if "drive_engine" in inspect.signature(run_scenario).parameters else {}

def mut(d, name):
    d = copy.deepcopy(d)
    ev, ib = d.get("events", []), d.get("initial_beliefs", [])
    if name == "no_user":        d["events"] = [e for e in ev if not e.get("is_user_trigger")]
    elif name == "no_obs":       d["events"] = []
    elif name == "no_seed_commit": d["initial_beliefs"] = [b for b in ib if b.get("kind") != "commitment"]
    elif name == "no_seed_all":  d["initial_beliefs"] = []; d.setdefault("metadata", {})["contradictions"] = []
    elif name == "no_seed_commit_no_user":
        d["initial_beliefs"] = [b for b in ib if b.get("kind") != "commitment"]
        d["events"] = [e for e in ev if not e.get("is_user_trigger")]
    elif name in ("calm_no_obs", "calm_no_user"):
        d = mut(d, "calm_seed")
        d["events"] = [] if name == "calm_no_obs" else [e for e in d["events"] if not e.get("is_user_trigger")]
    elif name == "calm_seed":    # same structure, beliefs already resolved: low uncertainty, commitment closed
        for b in d["initial_beliefs"]:
            b["uncertainty"] = 0.05
            if b.get("distribution"):
                k = next(iter(b["distribution"])); b["distribution"] = {k: 1.0}
            if b.get("kind") == "commitment": b.setdefault("metadata", {})["status"] = "closed"
        d.setdefault("metadata", {})["contradictions"] = []
    return d

CONDS = ["full", "no_user", "no_obs", "no_seed_commit", "no_seed_all", "no_seed_commit_no_user", "calm_seed", "calm_no_user", "calm_no_obs"]
tmp = Path(tempfile.mkdtemp())
res = collections.defaultdict(list)
for p in paths:
    base = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    for c in CONDS:
        d = base if c == "full" else mut(base, c)
        f = tmp / f"{base['id']}__{c}.yaml"; f.write_text(yaml.safe_dump(d, allow_unicode=True), encoding="utf-8")
        for sd in seeds:
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    r = run_scenario(f, traces_dir=tmp / "tr", seed=sd, **kw)
                ini = r["initiative"]
                out = "abstain" if ini.abstained else f"{ini.candidate.kind.value}:{ini.candidate.target_belief_id}"
                res[(base["id"], c)].append((out, r["decision"].outcome.value, round(r["twin_result"].eoi, 2)))
            except Exception as e:
                res[(base["id"], c)].append((f"ERR {type(e).__name__}: {e}"[:60], "-", "-"))
detail = {k: v for k, v in res.items()}
json.dump({f"{k[0]}|{k[1]}": v for k, v in res.items()}, open(tmp / "res.json", "w"))
ids = sorted({k[0] for k in res})
print(f"engine={engine} seeds={seeds}")
for c in CONDS:
    same = 0; tot = 0; outs = collections.Counter()
    for i in ids:
        f0 = [x[0] for x in res[(i, "full")]]; fc = [x[0] for x in res[(i, c)]]
        same += sum(a == b for a, b in zip(f0, fc)); tot += len(fc)
        outs.update(fc)
    top = ", ".join(f"{k}x{v}" for k, v in outs.most_common(3))
    print(f"  {c:24s} initiative identical to full: {same}/{tot}   outputs: {top}")

if "--detail" in sys.argv or True:
    print("  per-scenario (first seed): " )
    for i in ids:
        print("   ", i, " | ".join(f"{c}={res[(i,c)][0][0].replace('ask_question:belief-','Q:')}/{res[(i,c)][0][1]}" for c in CONDS))
