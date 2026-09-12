"""Operational lemma battery — maps PRE_PROOF.md lemmas to runnable experiments."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "lib"
TOPO = ROOT / "topo_lang"
HARNESS = ROOT / "harnesses"
ARTIFACTS = ROOT / "artifacts"
EXAMPLES = TOPO / "examples"

for p in (LIB, TOPO, HARNESS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from hdc import cosine  # noqa: E402
from interpreter import TopoInterpreter  # noqa: E402
from parser import load_topo  # noqa: E402
from program import TopoNode, TopoProgram  # noqa: E402
from topology import p_adic_distance  # noqa: E402
from t_kai_06_padic_clustering import run_experiment as run_padic  # noqa: E402
from t_kai_08_syntax_vs_semantics import run_experiment as run_t08  # noqa: E402
from t_kai_09_attention_vs_diffusion import run_experiment as run_t09  # noqa: E402
from t_kai_10_nd_quasi_orthogonality import run_experiment as run_t10  # noqa: E402

DATE = date.today().isoformat()
ARTIFACT_ID = f"PRE_PROOF_{DATE}"


def _lemma_topo_2_geodesic_mass(*, seed: int = 42) -> dict[str, Any]:
    """L-TOPO-2: closed loop vs linear re-entry mass preservation."""
    program = load_topo(EXAMPLES / "loop_geodesic.topo")
    interpreter = TopoInterpreter(program)

    loop_trace = interpreter.execute()
    loop_mass = float(np.linalg.norm(loop_trace.final_vector))
    initial = np.array([1.0, 0.0, 0.0])
    initial_mass = float(np.linalg.norm(initial))

    # Linear re-entry: repeat geodesic path without loop edge, reset packet each lap
    path_no_loop = ["init", "increment", "check", "body"]
    packet = initial.copy()
    for _ in range(3):
        packet = initial.copy()  # linear re-entry resets state
        for name in path_no_loop:
            packet = interpreter._transform(name, packet)
    linear_mass = float(np.linalg.norm(packet))

    loop_retention = loop_mass / initial_mass
    linear_retention = linear_mass / initial_mass
    margin = 0.05
    passed = loop_retention > linear_retention + margin

    return {
        "lemma_id": "L-TOPO-2",
        "hypothesis": "Closed geodesic preserves activation mass better than linear re-entry",
        "loop_mass_retention": loop_retention,
        "linear_reentry_mass_retention": linear_retention,
        "margin_required": margin,
        "pass": passed,
    }


def _lemma_topo_3_braid_classifier(*, seed: int = 42) -> dict[str, Any]:
    """L-TOPO-3: braid crossing activation pattern distinguishes branch vs merge."""
    program = load_topo(EXAMPLES / "if_then_else.topo")
    interpreter = TopoInterpreter(program)

    # Positive branch: boost branch_then param
    prog_then = TopoProgram(
        name=program.name,
        curvature=program.curvature,
        layer=program.layer,
        edges=program.edges,
        entry=program.entry,
        exit="branch_then",
    )
    for name, node in program.nodes.items():
        prog_then.add_node(
            TopoNode(
                name=node.name,
                kind=node.kind,
                position=node.position.copy(),
                phase=node.phase,
                glyph=node.glyph,
                param=node.param,
            )
        )

    prog_else = TopoProgram(
        name=program.name + "_else",
        curvature=program.curvature,
        layer=program.layer,
        edges=program.edges,
        entry=program.entry,
        exit="branch_else",
    )
    for name, node in program.nodes.items():
        prog_else.add_node(
            TopoNode(
                name=node.name,
                kind=node.kind,
                position=node.position.copy(),
                phase=node.phase,
                glyph=node.glyph,
                param=node.param,
            )
        )

    merge_prog = load_topo(EXAMPLES / "horizontal_compose.topo")
    trace_then = TopoInterpreter(prog_then).execute()
    trace_else = TopoInterpreter(prog_else).execute()
    trace_merge = TopoInterpreter(merge_prog).execute()

    sig_then = np.concatenate(trace_then.activations[-1:])
    sig_else = np.concatenate(trace_else.activations[-1:])
    sig_merge = np.concatenate(trace_merge.activations[-1:])

    sep_then_merge = 1.0 - cosine(sig_then, sig_merge)
    sep_else_merge = 1.0 - cosine(sig_else, sig_merge)
    sep_branches = 1.0 - cosine(sig_then, sig_else)

    threshold = 0.15
    passed = sep_then_merge > threshold and sep_else_merge > threshold and sep_branches > threshold

    return {
        "lemma_id": "L-TOPO-3",
        "hypothesis": "Braid crossing branch patterns distinguishable from path merge",
        "separation_then_vs_merge": sep_then_merge,
        "separation_else_vs_merge": sep_else_merge,
        "separation_then_vs_else": sep_branches,
        "threshold_min_separation": threshold,
        "pass": passed,
    }


def _lemma_topo_4_hierarchy_padic(*, prime: int = 7) -> dict[str, Any]:
    """L-TOPO-4: p-adic distances reflect hierarchical program structure."""
    hierarchy = {
        "root": 1,
        "module_a": 7,
        "module_b": 49,
        "fn_a1": 7 * 7,
        "fn_a2": 7 * 7 * 7,
        "fn_b1": 49 * 7,
        "leaf_unrelated": 11,
    }
    parent_child = [
        ("root", "module_a"),
        ("root", "module_b"),
        ("module_a", "fn_a1"),
        ("module_a", "fn_a2"),
        ("module_b", "fn_b1"),
    ]
    unrelated = [
        ("fn_a1", "fn_b1"),
        ("fn_a2", "leaf_unrelated"),
        ("module_a", "leaf_unrelated"),
    ]

    pc_dists = [p_adic_distance(hierarchy[a], hierarchy[b], prime) for a, b in parent_child]
    un_dists = [p_adic_distance(hierarchy[a], hierarchy[b], prime) for a, b in unrelated]
    mean_pc = float(np.mean(pc_dists))
    mean_un = float(np.mean(un_dists))
    passed = mean_pc < mean_un

    padic_base = run_padic()
    return {
        "lemma_id": "L-TOPO-4",
        "hypothesis": "Ultrametric p-adic clustering matches hierarchical program structure",
        "prime": prime,
        "hierarchy_encodings": hierarchy,
        "mean_parent_child_distance": mean_pc,
        "mean_unrelated_distance": mean_un,
        "ultrametric_on_theory_concepts": padic_base["ultrametric_holds"],
        "pass": passed and padic_base["ultrametric_holds"],
    }


def _lemma_topo_1_from_t08(t08: dict[str, Any]) -> dict[str, Any]:
    agg = t08["aggregate"]
    margin = 0.1
    passed = (
        agg["mean_topological_shuffle_similarity"]
        >= agg["mean_linear_shuffle_similarity"] + margin
        and agg["topo_wins_stability_count"] >= 4
    )
    return {
        "lemma_id": "L-TOPO-1",
        "hypothesis": "Topo encoding has lower semantic drift under node permutation than linear shuffle",
        "mean_linear_shuffle_similarity": agg["mean_linear_shuffle_similarity"],
        "mean_topo_shuffle_similarity": agg["mean_topological_shuffle_similarity"],
        "topo_wins_count": agg["topo_wins_stability_count"],
        "harness": "T-KAI-08",
        "pass": passed,
    }


def run_lemma_battery(*, seed: int = 42) -> dict[str, Any]:
    t08 = run_t08(seed=seed)
    t09 = run_t09(seed=seed)
    t10 = run_t10(seed=seed)

    lemmas = [
        _lemma_topo_1_from_t08(t08),
        _lemma_topo_2_geodesic_mass(seed=seed),
        _lemma_topo_3_braid_classifier(seed=seed),
        _lemma_topo_4_hierarchy_padic(),
        {
            "lemma_id": "L-MAT-1",
            **t09["lemma_results"]["L-MAT-1"],
            "harness": "T-KAI-09",
        },
        {
            "lemma_id": "L-MAT-2",
            **t09["lemma_results"]["L-MAT-2"],
            "harness": "T-KAI-09",
        },
    ]

    pass_count = sum(1 for lm in lemmas if lm.get("pass"))
    return {
        "artifact_id": ARTIFACT_ID,
        "date": DATE,
        "strand": "kairologos_standalone",
        "framework": "PRE_PROOF operational lemmas (empirical, not QED)",
        "seed": seed,
        "lemmas": lemmas,
        "summary": {
            "total": len(lemmas),
            "passed": pass_count,
            "failed": len(lemmas) - pass_count,
            "pass_rate": pass_count / len(lemmas),
        },
        "harness_refs": {
            "T-KAI-08": t08["artifact_id"],
            "T-KAI-09": t09["artifact_id"],
            "T-KAI-10": t10["artifact_id"],
        },
    }


def write_artifacts(payload: dict[str, Any]) -> tuple[Path, Path]:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    json_path = ARTIFACTS / f"{ARTIFACT_ID}.json"
    md_path = ARTIFACTS / f"{ARTIFACT_ID}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# {ARTIFACT_ID}",
        "",
        "**Framework:** PRE_PROOF operational lemmas",
        "",
        "## Lemma results",
        "",
        "| Lemma | Pass |",
        "|-------|------|",
    ]
    for lm in payload["lemmas"]:
        lines.append(f"| {lm['lemma_id']} | **{lm.get('pass', False)}** |")
    lines.extend(
        [
            "",
            f"**Pass rate:** {payload['summary']['passed']}/{payload['summary']['total']}",
            "",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> dict[str, Any]:
    payload = run_lemma_battery()
    json_path, md_path = write_artifacts(payload)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Lemma pass rate: {payload['summary']['passed']}/{payload['summary']['total']}")
    return payload


if __name__ == "__main__":
    main()
