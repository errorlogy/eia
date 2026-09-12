"""T-KAI-08 — Syntax vs semantics: linear pseudo-C vs 3D topological graph."""

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
ARTIFACTS = ROOT / "artifacts"
EXAMPLES = TOPO / "examples"

for p in (LIB, TOPO):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from hdc import bind, bundle, cosine, random_bipolar  # noqa: E402
from interpreter import TopoInterpreter  # noqa: E402
from parser import load_topo  # noqa: E402
from program import TopoNode, TopoProgram  # noqa: E402

HARNESS_ID = "T-KAI-08"
DATE = date.today().isoformat()
ARTIFACT_ID = f"{HARNESS_ID}_{DATE}"
HDC_DIM = 512


def levenshtein(a: list[str], b: list[str]) -> int:
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[-1]


def pseudo_c_tokens(task_id: str) -> list[str]:
    catalog: dict[str, list[str]] = {
        "if_then_else": [
            "if", "x", ">", "0", "then", "return", "x", "else", "return", "neg", "x",
        ],
        "loop_geodesic": [
            "init", "i", "=", "0", "while", "i", "<", "3", "i", "++", "sum", "+=", "i",
        ],
        "function_lift": ["y", "=", "g", "(", "f", "(", "x", ")", ")",],
        "horizontal_compose": ["A", ";", "B", ";", "C",],
        "borromeo_bind": ["bind", "A", "B", "C", "triad", "lock",],
    }
    return catalog[task_id]


def linear_representation_dimension(tokens: list[str]) -> int:
    return len(tokens)


def topo_representation_dimension(program: TopoProgram) -> int:
    return program.representation_dimension()


def perturb_tokens(tokens: list[str], *, seed: int) -> list[str]:
    rng = np.random.default_rng(seed)
    out = tokens.copy()
    if len(out) < 2:
        return out
    i, j = rng.choice(len(out), size=2, replace=False)
    out[i], out[j] = out[j], out[i]
    return out


def perturb_topo_positions(program: TopoProgram, *, seed: int) -> TopoProgram:
    rng = np.random.default_rng(seed)
    names = list(program.nodes.keys())
    if len(names) < 2:
        return program
    i, j = rng.choice(len(names), size=2, replace=False)
    a, b = names[i], names[j]
    cloned = TopoProgram(
        name=program.name + "_perturbed",
        curvature=program.curvature,
        layer=program.layer,
        edges=program.edges,
        entry=program.entry,
        exit=program.exit,
    )
    for name, node in program.nodes.items():
        pos = node.position.copy()
        if name == a:
            pos = program.nodes[b].position.copy()
        elif name == b:
            pos = program.nodes[a].position.copy()
        cloned.add_node(
            TopoNode(
                name=node.name,
                kind=node.kind,
                position=pos,
                phase=node.phase,
                glyph=node.glyph,
                param=node.param,
            )
        )
    return cloned


def simulate_c_semantics(tokens: list[str]) -> list[str]:
    """Minimal trace model for pseudo-C — order-sensitive token projection."""
    trace: list[str] = []
    for tok in tokens:
        if tok in {"if", "while", "return", "else", "then"}:
            trace.append(f"ctrl:{tok}")
        elif tok.isidentifier() or tok in {"+", "-", ">", "<", "="}:
            trace.append(f"data:{tok}")
        else:
            trace.append(f"sym:{tok}")
    return trace


def simulate_topo_semantics(program: TopoProgram) -> list[str]:
    trace = TopoInterpreter(program).execute()
    return [f"{name}:{trace.phases[name]:.2f}" for name in trace.path]


def _permute(vec: np.ndarray, k: int) -> np.ndarray:
    return np.roll(vec, k % HDC_DIM)


def linear_hdc_vector(tokens: list[str], *, seed: int) -> np.ndarray:
    """Order-sensitive sequential binding (1D syntax)."""
    rng = np.random.default_rng(seed)
    token_vecs = {tok: random_bipolar(rng, HDC_DIM) for tok in tokens}
    acc = random_bipolar(rng, HDC_DIM)
    for idx, tok in enumerate(tokens):
        acc = bind(acc, _permute(token_vecs[tok], idx))
    return acc


def topo_hdc_vector(program: TopoProgram, *, seed: int) -> np.ndarray:
    """Position-anchored binding: semantics follow coordinates, not identifier strings."""
    pairs: list[np.ndarray] = []
    for node in sorted(
        program.nodes.values(),
        key=lambda n: (float(n.position[0]), float(n.position[1]), float(n.position[2]), n.phase),
    ):
        pos_key = np.array(
            [node.position[0], node.position[1], node.position[2], node.phase, node.param],
            dtype=float,
        )
        pos_seed = (seed + int(np.abs(np.round(pos_key * 1000)).sum())) % (2**31 - 1)
        pos_rng = np.random.default_rng(pos_seed)
        pairs.append(random_bipolar(pos_rng, HDC_DIM))
    return bundle(pairs)


def meaning_stability_linear(tokens: list[str], *, seed: int, n_shuffles: int = 32) -> dict[str, float]:
    base = linear_hdc_vector(tokens, seed=seed)
    rng = np.random.default_rng(seed)
    sims: list[float] = []
    for _ in range(n_shuffles):
        shuffled = tokens.copy()
        rng.shuffle(shuffled)
        sims.append(cosine(base, linear_hdc_vector(shuffled, seed=seed)))
    return {
        "mean_similarity": float(np.mean(sims)),
        "min_similarity": float(np.min(sims)),
        "max_similarity": float(np.max(sims)),
    }


def meaning_stability_topo(program: TopoProgram, *, seed: int, n_shuffles: int = 32) -> dict[str, float]:
    base = topo_hdc_vector(program, seed=seed)
    rng = np.random.default_rng(seed)
    sims: list[float] = []
    names = list(program.nodes.keys())
    for _ in range(n_shuffles):
        perm = rng.permutation(len(names))
        shuffled = TopoProgram(
            name=program.name,
            curvature=program.curvature,
            layer=program.layer,
            edges=program.edges,
            entry=program.entry,
            exit=program.exit,
        )
        old_nodes = list(program.nodes.values())
        for new_idx, old_idx in enumerate(perm):
            old = old_nodes[old_idx]
            shuffled.add_node(
                TopoNode(
                    name=names[new_idx],
                    kind=old.kind,
                    position=old.position.copy(),
                    phase=old.phase,
                    glyph=old.glyph,
                    param=old.param,
                )
            )
        sims.append(cosine(base, topo_hdc_vector(shuffled, seed=seed)))
    return {
        "mean_similarity": float(np.mean(sims)),
        "min_similarity": float(np.min(sims)),
        "max_similarity": float(np.max(sims)),
    }


def evaluate_task(task_id: str, topo_path: Path, *, seed: int = 42) -> dict[str, Any]:
    program = load_topo(topo_path)
    tokens = pseudo_c_tokens(task_id)

    base_c_trace = simulate_c_semantics(tokens)
    base_t_trace = simulate_topo_semantics(program)

    perturbed_tokens = perturb_tokens(tokens, seed=seed)
    perturbed_program = perturb_topo_positions(program, seed=seed)

    pert_c_trace = simulate_c_semantics(perturbed_tokens)
    pert_t_trace = simulate_topo_semantics(perturbed_program)

    c_edit = levenshtein(base_c_trace, pert_c_trace) / max(len(base_c_trace), 1)
    t_edit = levenshtein(base_t_trace, pert_t_trace) / max(len(base_t_trace), 1)

    c_stability = meaning_stability_linear(tokens, seed=seed)
    t_stability = meaning_stability_topo(program, seed=seed)

    return {
        "task_id": task_id,
        "topo_file": str(topo_path.name),
        "linear": {
            "tokens": tokens,
            "representation_dimension": linear_representation_dimension(tokens),
            "perturbed_edit_distance_norm": c_edit,
            "meaning_stability_after_shuffle": c_stability,
            "base_trace": base_c_trace,
            "perturbed_trace": pert_c_trace,
        },
        "topological": {
            "representation_dimension": topo_representation_dimension(program),
            "layer": program.layer,
            "curvature": program.curvature,
            "node_count": len(program.nodes),
            "edge_count": len(program.edges),
            "perturbed_edit_distance_norm": t_edit,
            "meaning_stability_after_shuffle": t_stability,
            "base_trace": base_t_trace,
            "perturbed_trace": pert_t_trace,
            "execution": {
                "path": TopoInterpreter(program).execute().path,
                "order_parameter": TopoInterpreter(program).execute().order_parameter,
            },
        },
        "comparison": {
            "dimension_ratio_topo_over_linear": topo_representation_dimension(program)
            / max(linear_representation_dimension(tokens), 1),
            "topo_more_stable_under_shuffle": t_stability["mean_similarity"]
            > c_stability["mean_similarity"],
            "topo_lower_perturbation_edit": t_edit < c_edit,
        },
    }


def run_experiment(*, seed: int = 42) -> dict[str, Any]:
    tasks = [
        ("if_then_else", EXAMPLES / "if_then_else.topo"),
        ("loop_geodesic", EXAMPLES / "loop_geodesic.topo"),
        ("function_lift", EXAMPLES / "function_lift.topo"),
        ("horizontal_compose", EXAMPLES / "horizontal_compose.topo"),
        ("borromeo_bind", EXAMPLES / "borromeo_bind.topo"),
    ]
    results = [evaluate_task(task_id, path, seed=seed) for task_id, path in tasks]

    mean_c_edit = float(np.mean([r["linear"]["perturbed_edit_distance_norm"] for r in results]))
    mean_t_edit = float(np.mean([r["topological"]["perturbed_edit_distance_norm"] for r in results]))
    mean_c_stab = float(
        np.mean([r["linear"]["meaning_stability_after_shuffle"]["mean_similarity"] for r in results])
    )
    mean_t_stab = float(
        np.mean([r["topological"]["meaning_stability_after_shuffle"]["mean_similarity"] for r in results])
    )

    return {
        "harness_id": HARNESS_ID,
        "artifact_id": ARTIFACT_ID,
        "date": DATE,
        "strand": "kairologos_standalone",
        "theory_section": "§1.2 semiotic geometry — syntax motifs vs spatial binding",
        "seed": seed,
        "hdc_dim": HDC_DIM,
        "tasks": results,
        "aggregate": {
            "mean_linear_edit_distance_norm": mean_c_edit,
            "mean_topological_edit_distance_norm": mean_t_edit,
            "mean_linear_shuffle_similarity": mean_c_stab,
            "mean_topological_shuffle_similarity": mean_t_stab,
            "topo_wins_stability_count": sum(
                1 for r in results if r["comparison"]["topo_more_stable_under_shuffle"]
            ),
            "topo_wins_perturbation_count": sum(
                1 for r in results if r["comparison"]["topo_lower_perturbation_edit"]
            ),
        },
        "open_questions": {
            "does_spatial_encoding_reduce_perturbation_sensitivity": mean_t_edit < mean_c_edit,
            "does_label_shuffle_preserve_topo_bundle_more": mean_t_stab > mean_c_stab,
            "claims_turing_transcendence": False,
        },
        "interpretation_notes": [
            "Prototype comparison only — pseudo-C traces are toy projections, not a compiler.",
            "Topological perturbation swaps node positions, not connectivity — tests geometry-first semantics.",
            "HDC shuffle test permutes symbol order; high similarity does NOT prove consciousness or AGI.",
            "Higher representation_dimension for topo is expected; question is stability, not compression.",
        ],
    }


def write_artifacts(payload: dict[str, Any]) -> tuple[Path, Path]:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    json_path = ARTIFACTS / f"{ARTIFACT_ID}.json"
    md_path = ARTIFACTS / f"{ARTIFACT_ID}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    agg = payload["aggregate"]
    lines = [
        f"# {ARTIFACT_ID}",
        "",
        "**Strand:** Kairologos standalone (not EIA)",
        "",
        "## Question",
        "For the same logical motif, does 3D topological encoding show higher meaning stability",
        "under label shuffle and lower semantic drift under spatial perturbation than pseudo-C?",
        "",
        "## Aggregate",
        f"- Mean linear edit distance (normalized): **{agg['mean_linear_edit_distance_norm']:.4f}**",
        f"- Mean topological edit distance: **{agg['mean_topological_edit_distance_norm']:.4f}**",
        f"- Mean linear HDC shuffle similarity: **{agg['mean_linear_shuffle_similarity']:.4f}**",
        f"- Mean topological HDC shuffle similarity: **{agg['mean_topological_shuffle_similarity']:.4f}**",
        f"- Tasks where topo bundle more stable: **{agg['topo_wins_stability_count']}/5**",
        f"- Tasks where topo lower perturbation edit: **{agg['topo_wins_perturbation_count']}/5**",
        "",
        "## Tasks",
    ]
    for task in payload["tasks"]:
        lines.extend(
            [
                f"### {task['task_id']}",
                f"- Linear dim: {task['linear']['representation_dimension']} | "
                f"Topo dim: {task['topological']['representation_dimension']}",
                f"- Linear edit: {task['linear']['perturbed_edit_distance_norm']:.3f} | "
                f"Topo edit: {task['topological']['perturbed_edit_distance_norm']:.3f}",
                "",
            ]
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> dict[str, Any]:
    payload = run_experiment()
    json_path, md_path = write_artifacts(payload)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return payload


if __name__ == "__main__":
    main()
