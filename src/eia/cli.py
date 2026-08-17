"""EIA CLI — run, replay, demo."""

from __future__ import annotations

import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from eia.audit import CausalTrace, TraceNodeKind
from eia.beliefs.visualize import render_field_heatmap
from eia.pipeline import run_scenario
from eia.schemas.contact import ContactOutcome

console = Console()


def _default_scenario() -> Path:
    return Path(__file__).resolve().parents[2] / "scenarios" / "twin_world_001.yaml"


@click.group()
@click.version_option(package_name="eia")
def main() -> None:
    """Endogenous Initiative Architecture — MVP-0 CLI."""


@main.command()
@click.option("--scenario", "scenario_path", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--traces-dir", type=click.Path(path_type=Path), default="traces")
def demo(scenario_path: Path | None, traces_dir: Path) -> None:
    """Run twin_world_001 — one endogenous question WITHOUT user prompt."""
    path = scenario_path or _default_scenario()
    console.print(Panel.fit("[bold]EIA MVP-0 Demo[/bold]\nEndogenous Initiative Architecture", border_style="cyan"))

    result = run_scenario(path, traces_dir=traces_dir)
    loop = result["loop"]
    motivation = result["motivation"]
    initiative = result["initiative"]
    decision = result["decision"]
    twin = result["twin_result"]
    namm = result["namm_intent"]

    console.print("\n[bold yellow]BeliefField state before initiative:[/bold yellow]")
    console.print(render_field_heatmap(loop.field))

    drive_table = Table(title="Drive Tensions (structural, not embedding-based)")
    drive_table.add_column("Drive")
    drive_table.add_column("Intensity", justify="right")
    drive_table.add_column("Error", justify="right")
    drive_table.add_column("Explanation")
    for sig in motivation.signals:
        drive_table.add_row(
            sig.drive.value,
            f"{sig.intensity:.3f}",
            f"{sig.error_term:.3f}",
            sig.explanation[:60],
        )
    console.print(drive_table)

    if namm:
        console.print(
            Panel(
                f"[green]NAMM stub fired[/green]\n"
                f"internal_experiment intent: {namm.intent_id}\n"
                f"epistemic intensity: {namm.intensity:.3f}\n"
                f"certificate placeholder: {namm.certificate_placeholder}",
                title="NAMM Adapter",
                border_style="green",
            )
        )

    if initiative.abstained:
        q_text = "(abstained)"
    else:
        q_text = initiative.candidate.question_text or initiative.candidate.kind.value

    console.print(
        Panel(
            f"[bold]Initiative:[/bold] {initiative.candidate.kind.value}\n"
            f"[bold]Abstained:[/bold] {initiative.abstained}\n"
            f"[bold]Question:[/bold] {q_text}\n"
            f"[bold]EVSI:[/bold] {initiative.evsi:.3f}\n"
            f"[bold]Competing candidates:[/bold] {len(initiative.competing_candidate_ids)}",
            title="Intention Genesis",
            border_style="magenta",
        )
    )

    outcome_color = "green" if decision.outcome == ContactOutcome.SEND_NOW else "red"
    console.print(
        Panel(
            f"[bold]Outcome:[/bold] [{outcome_color}]{decision.outcome.value}[/{outcome_color}]\n"
            f"[bold]Contact score:[/bold] {decision.contact_score:.3f}\n"
            f"[bold]Reason:[/bold] {decision.reason}\n"
            f"[bold]Budget remaining:[/bold] {decision.budget_remaining}",
            title="Contact Governor (independent)",
            border_style=outcome_color,
        )
    )

    console.print(
        Panel(
            f"[bold]EOI (Endogenous Origin Index):[/bold] {twin.eoi:.3f}\n"
            f"[bold]Semantic match (twin vs original):[/bold] {twin.semantic_match:.3f}\n"
            f"[bold]Removed user events:[/bold] {len(twin.removed_user_event_ids)}\n"
            f"[bold]Twin abstained:[/bold] {twin.abstained_in_twin}",
            title="Counterfactual Twin Run",
            border_style="blue",
        )
    )

    console.print(f"\n[dim]Causal trace exported:[/dim] {result['trace_path']}")
    console.print("[dim]Replay with:[/dim] eia replay --trace " + str(result["trace_path"]))


@main.command()
@click.option("--scenario", "scenario_path", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--traces-dir", type=click.Path(path_type=Path), default="traces")
def run(scenario_path: Path | None, traces_dir: Path) -> None:
    """Run a scenario (same as demo, minimal output)."""
    path = scenario_path or _default_scenario()
    result = run_scenario(path, traces_dir=traces_dir)
    console.print(json.dumps({
        "trace_id": result["loop"].trace.trace_id,
        "eoi": result["twin_result"].eoi,
        "initiative_abstained": result["initiative"].abstained,
        "contact_outcome": result["decision"].outcome.value,
        "trace_path": str(result["trace_path"]),
    }, indent=2))


@main.command()
@click.option("--trace", "trace_path", required=True, type=click.Path(exists=True, path_type=Path))
def replay(trace_path: Path) -> None:
    """Deterministic replay of a causal trace JSONL."""
    trace = CausalTrace.load_jsonl(trace_path)

    table = Table(title=f"Causal Trace Replay: {trace.trace_id}")
    table.add_column("#", justify="right")
    table.add_column("Kind")
    table.add_column("ID")
    table.add_column("Summary")

    for i, node in enumerate(trace.nodes):
        summary = _summarize_node(node)
        table.add_row(str(i + 1), node.kind.value, node.id[:24], summary)

    console.print(table)
    console.print(f"\n[bold]Edges:[/bold] {len(trace.edges)} causal links")

    eoi_nodes = [n for n in trace.nodes if n.kind == TraceNodeKind.EOI_SCORE]
    if eoi_nodes:
        eoi = eoi_nodes[-1].payload.get("eoi", 0)
        console.print(f"[bold green]EOI from trace:[/bold green] {eoi:.3f}")


def _summarize_node(node) -> str:
    p = node.payload
    if node.kind == TraceNodeKind.OBSERVATION:
        return f"topic={p.get('topic', '?')} user={p.get('is_user_trigger', False)}"
    if node.kind == TraceNodeKind.MOTIVATION:
        drives = p.get("signals", [])
        top = max(drives, key=lambda s: s.get("intensity", 0)) if drives else {}
        return f"dominant={p.get('dominant_drive', '?')} top_intensity={top.get('intensity', 0):.2f}"
    if node.kind == TraceNodeKind.INITIATIVE:
        c = p.get("candidate", {})
        return f"kind={c.get('kind', '?')} abstained={p.get('abstained', False)}"
    if node.kind == TraceNodeKind.CONTACT_DECISION:
        return f"outcome={p.get('outcome', '?')} score={p.get('contact_score', 0):.2f}"
    if node.kind == TraceNodeKind.EOI_SCORE:
        return f"eoi={p.get('eoi', 0):.3f}"
    return str(list(p.keys())[:3])


if __name__ == "__main__":
    main()
