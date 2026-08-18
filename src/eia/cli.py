"""EIA CLI — run, replay, demo."""

from __future__ import annotations

import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from eia.audit import CausalTrace, TraceNodeKind
from eia.audit.replay import ReplayMetadataError, re_execute_trace
from eia.beliefs.visualize import render_field_heatmap
from eia.experiment.baseline import BaselineCondition, load_baseline_from_config
from eia.pipeline import run_scenario
from eia.runtime.daemon import DaemonConfig, DaemonRuntime, run_daemon_tick
from eia.runtime.state_store import StateStore
from eia.scheduler import PipelineStage
from eia.schemas.contact import ContactOutcome

console = Console()


def _default_scenario() -> Path:
    return Path(__file__).resolve().parents[2] / "scenarios" / "twin_world_001.yaml"


def _pipeline_scenario() -> Path:
    return Path(__file__).resolve().parents[2] / "scenarios" / "pipeline_demo_002.yaml"


STAGE_ORDER = [
    PipelineStage.OBSERVATION_INGEST,
    PipelineStage.SENSE_MAKING,
    PipelineStage.MOTIVE_FORMATION,
    PipelineStage.INTENTION_GENESIS,
    PipelineStage.INITIATIVE_EMISSION,
    PipelineStage.CONTACT_GOVERNOR,
]

STAGE_LABELS = {
    PipelineStage.OBSERVATION_INGEST: "1. ObservationIngest",
    PipelineStage.SENSE_MAKING: "2. SenseMaking (BeliefField)",
    PipelineStage.MOTIVE_FORMATION: "3. MotiveFormation (DriveEngine)",
    PipelineStage.INTENTION_GENESIS: "4. IntentionGenesis",
    PipelineStage.INITIATIVE_EMISSION: "5. InitiativeEmission",
    PipelineStage.CONTACT_GOVERNOR: "6. ContactGovernor",
}


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
    auth = result["authentic_verdict"]
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

    auth_color = "green" if auth.is_authentic else "yellow"
    codes = ", ".join(c.value for c in auth.reason_codes[:6])
    console.print(
        Panel(
            f"[bold]Authentic:[/bold] [{auth_color}]{auth.is_authentic}[/{auth_color}]\n"
            f"[bold]Class:[/bold] {auth.initiative_class}\n"
            f"[bold]Summary:[/bold] {auth.summary}\n"
            f"[bold]Codes:[/bold] {codes}",
            title="Authentic Reason Discriminator",
            border_style=auth_color,
        )
    )

    console.print(f"\n[dim]Causal trace exported:[/dim] {result['trace_path']}")
    console.print("[dim]Replay with:[/dim] eia replay --trace " + str(result["trace_path"]))


@main.command()
@click.option("--scenario", "scenario_path", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--traces-dir", type=click.Path(path_type=Path), default="traces")
def pipeline(scenario_path: Path | None, traces_dir: Path) -> None:
    """Run full 5-stage pipeline with labeled trace and NAMM hooks."""
    path = scenario_path or _pipeline_scenario()
    console.print(
        Panel.fit(
            "[bold]EIA Pipeline Demo[/bold]\n"
            "ObservationIngest → SenseMaking → MotiveFormation → "
            "IntentionGenesis → InitiativeEmission → ContactGovernor",
            border_style="cyan",
        )
    )

    result = run_scenario(path, traces_dir=traces_dir)
    loop = result["loop"]
    stage_log = result["stage_log"]

    pipeline_table = Table(title="Five-Stage Cognitive Pipeline")
    pipeline_table.add_column("Stage")
    pipeline_table.add_column("Summary")
    pipeline_table.add_column("NAMM / Loops", overflow="fold")

    seen_stages: set[str] = set()
    for stage in STAGE_ORDER:
        entries = [s for s in stage_log if s.stage == stage]
        if not entries:
            continue
        last = entries[-1]
        seen_stages.add(stage.value)
        loops = last.payload.get("loop_schedule", {})
        active = ", ".join(loops.get("active_loops", [])[:4])
        namm = ", ".join(loops.get("namm_experiments", []))
        namm_hooks = last.payload.get("namm_hooks") or []
        if last.payload.get("namm_hook"):
            namm_hooks = namm_hooks + [last.payload["namm_hook"]]
        hook_str = ", ".join(namm_hooks) if namm_hooks else namm
        pipeline_table.add_row(
            STAGE_LABELS.get(stage, stage.value),
            last.summary[:70],
            f"{hook_str or '—'} [{active}]" if active else (hook_str or "—"),
        )

    console.print(pipeline_table)

    namm_nodes = [
        n for n in loop.trace.nodes if n.kind == TraceNodeKind.NAMM_HOOK
    ]
    if namm_nodes:
        console.print(
            Panel(
                "\n".join(
                    f"• {n.payload.get('namm_experiment_ref')}: "
                    f"{n.payload.get('artifact', n.payload.get('kind', ''))}"
                    for n in namm_nodes
                ),
                title="NAMM Artifact Hooks",
                border_style="green",
            )
        )

    console.print("\n[bold yellow]BeliefField after pipeline:[/bold yellow]")
    console.print(render_field_heatmap(loop.field))

    twin = result["twin_result"]
    auth = result["authentic_verdict"]
    console.print(
        Panel(
            f"[bold]EOI:[/bold] {twin.eoi:.3f} · "
            f"[bold]Contact:[/bold] {result['decision'].outcome.value}\n"
            f"[bold]Authentic reason:[/bold] {auth.is_authentic} ({auth.initiative_class})\n"
            f"[dim]Trace:[/dim] {result['trace_path']}",
            title="Outcome",
            border_style="blue",
        )
    )


@main.command()
@click.option("--scenario", "scenario_path", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--traces-dir", type=click.Path(path_type=Path), default="traces")
@click.option(
    "--baseline",
    type=click.Choice([b.value for b in BaselineCondition], case_sensitive=False),
    default=None,
    help="Experiment baseline condition (default: configs/experiment.json or full_eia).",
)
def run(scenario_path: Path | None, traces_dir: Path, baseline: str | None) -> None:
    """Run a scenario (same as demo, minimal output)."""
    path = scenario_path or _default_scenario()
    condition = BaselineCondition(baseline) if baseline else load_baseline_from_config()
    result = run_scenario(path, traces_dir=traces_dir, baseline=condition)
    console.print(json.dumps({
        "trace_id": result["loop"].trace.trace_id,
        "baseline": condition.value,
        "eoi": result["twin_result"].eoi,
        "authentic_reason": result["authentic_verdict"].is_authentic,
        "initiative_class": result["authentic_verdict"].initiative_class,
        "initiative_abstained": result["initiative"].abstained,
        "contact_outcome": result["decision"].outcome.value,
        "trace_path": str(result["trace_path"]),
    }, indent=2))


@main.command()
@click.option("--trace", "trace_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--re-execute",
    "re_execute",
    is_flag=True,
    default=False,
    help="Re-run simulator from trace metadata and compare traces.",
)
def replay(trace_path: Path, re_execute: bool) -> None:
    """Deterministic replay of a causal trace JSONL."""
    if re_execute:
        try:
            comparison = re_execute_trace(trace_path)
        except ReplayMetadataError as exc:
            console.print(f"[bold red]Cannot re-execute:[/bold red] {exc}")
            raise SystemExit(1) from exc

        color = "green" if comparison.matched else "red"
        console.print(
            Panel(
                f"[bold]Result:[/bold] [{color}]{comparison.summary}[/{color}]\n"
                f"[bold]Fingerprint (original):[/bold] {comparison.original_fingerprint}\n"
                f"[bold]Fingerprint (replay):[/bold] {comparison.replay_fingerprint}\n"
                f"[bold]EOI:[/bold] {comparison.eoi_original} → {comparison.eoi_replay} "
                f"({'match' if comparison.eoi_match else 'mismatch'})\n"
                f"[bold]Authentic reason:[/bold] "
                f"{comparison.auth_original} → {comparison.auth_replay} "
                f"({'match' if comparison.auth_match else 'mismatch'})",
                title="Replay Re-Execute",
                border_style=color,
            )
        )
        if comparison.key_node_diffs:
            console.print(
                "[yellow]Key node diffs:[/yellow] "
                + ", ".join(comparison.key_node_diffs)
            )
        if comparison.replay_trace_path:
            console.print(f"[dim]Replay trace:[/dim] {comparison.replay_trace_path}")
        raise SystemExit(0 if comparison.matched else 2)

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

    auth_nodes = [n for n in trace.nodes if n.kind == TraceNodeKind.AUTHENTIC_REASON]
    if auth_nodes:
        p = auth_nodes[-1].payload
        console.print(
            f"[bold green]Authentic reason:[/bold green] {p.get('is_authentic')} "
            f"({p.get('initiative_class')})"
        )


def _summarize_node(node) -> str:
    p = node.payload
    stage = p.get("pipeline_stage", "")
    prefix = f"[{stage}] " if stage else ""

    if node.kind in (TraceNodeKind.OBSERVATION, TraceNodeKind.OBSERVATION_INGEST):
        return prefix + f"topic={p.get('topic', '?')} user={p.get('is_user_trigger', False)}"
    if node.kind == TraceNodeKind.SENSE_MAKING:
        return prefix + p.get("comprehension_summary", p.get("stage_summary", ""))[:60]
    if node.kind in (TraceNodeKind.MOTIVATION, TraceNodeKind.MOTIVE_FORMATION):
        drives = p.get("signals", [])
        top = max(drives, key=lambda s: s.get("intensity", 0)) if drives else {}
        return prefix + (
            f"dominant={p.get('dominant_drive', '?')} "
            f"top_intensity={top.get('intensity', 0):.2f}"
        )
    if node.kind in (TraceNodeKind.INITIATIVE, TraceNodeKind.INTENTION_GENESIS):
        c = p.get("candidate", {})
        return prefix + f"kind={c.get('kind', '?')} abstained={p.get('abstained', False)}"
    if node.kind == TraceNodeKind.INITIATIVE_EMISSION:
        c = p.get("candidate", {})
        return prefix + f"emitted={c.get('kind', '?')}"
    if node.kind in (TraceNodeKind.CONTACT_DECISION, TraceNodeKind.CONTACT_GOVERNOR):
        return prefix + f"outcome={p.get('outcome', '?')} score={p.get('contact_score', 0):.2f}"
    if node.kind == TraceNodeKind.NAMM_HOOK:
        return prefix + f"ref={p.get('namm_experiment_ref')} {p.get('artifact', '')[:40]}"
    if node.kind == TraceNodeKind.EOI_SCORE:
        return f"eoi={p.get('eoi', 0):.3f}"
    if node.kind == TraceNodeKind.AUTHENTIC_REASON:
        return (
            f"authentic={p.get('is_authentic')} "
            f"class={p.get('initiative_class')} "
            f"{p.get('summary', '')[:40]}"
        )
    return prefix + str(list(p.keys())[:3])


@main.group()
def daemon() -> None:
    """Live contact daemon (MVP-0.5)."""


@daemon.command("start")
@click.option("--shadow/--live", default=True, help="Shadow mode (default) logs without HTTP send.")
@click.option("--foreground", is_flag=True, default=False, help="Run scheduler in foreground.")
def daemon_start(shadow: bool, foreground: bool) -> None:
    """Start live-stack daemon with APScheduler ticks."""
    if not shadow:
        import os

        if not os.environ.get("TELEGRAM_BOT_TOKEN") or not os.environ.get("TELEGRAM_CHAT_ID"):
            console.print(
                "[bold red]Live mode requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env[/bold red]"
            )
            raise SystemExit(1)
        store = StateStore()
        if not store.load().consent_telegram:
            console.print(
                "[bold red]Live mode requires consent — run:[/bold red] eia consent --enable-telegram"
            )
            raise SystemExit(1)

    cfg = DaemonConfig.from_env_and_yaml()
    runtime = DaemonRuntime(cfg, shadow_mode=shadow)
    mode_label = "shadow" if shadow else "live"
    console.print(
        Panel(
            f"[bold]Mode:[/bold] {mode_label}\n"
            f"[bold]Interval:[/bold] {cfg.interval_minutes} min\n"
            f"[bold]Workspace:[/bold] {cfg.workspace.resolve()}",
            title="EIA Daemon",
            border_style="cyan",
        )
    )
    runtime.start()
    console.print("[green]Daemon started.[/green] Use [bold]eia daemon status[/bold] to inspect.")
    if foreground:
        try:
            import time

            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            runtime.stop()
            console.print("[yellow]Daemon stopped.[/yellow]")
    else:
        console.print("[dim]Running in background — stop with SIGTERM or delete data/eia_daemon.pid[/dim]")


@daemon.command("status")
def daemon_status() -> None:
    """Show daemon PID, budget, consent, and quiet hours."""
    info = DaemonRuntime.status()
    table = Table(title="EIA Daemon Status")
    table.add_column("Key")
    table.add_column("Value")
    for key, value in info.items():
        table.add_row(key, str(value))
    console.print(table)


@main.command()
@click.option("--enable-telegram", is_flag=True, default=False, help="Grant Telegram contact consent.")
def consent(enable_telegram: bool) -> None:
    """Manage live contact consent flags."""
    store = StateStore()
    if enable_telegram:
        state = store.enable_telegram_consent()
        console.print(
            Panel(
                "[green]Telegram consent enabled.[/green]\n"
                "Live mode still requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.",
                title="Consent",
                border_style="green",
            )
        )
    else:
        state = store.load()
        console.print(
            json.dumps(
                {
                    "consent_telegram": state.consent_telegram,
                    "contact_budget": state.contact_budget,
                    "contacts_today": state.contacts_today,
                    "quiet_hours": f"{state.quiet_hours_start:02d}-{state.quiet_hours_end:02d}",
                },
                indent=2,
            )
        )


@main.command()
@click.option("--shadow/--live", default=True, help="Shadow mode (default).")
@click.option("--traces-dir", type=click.Path(path_type=Path), default=None)
def tick(shadow: bool, traces_dir: Path | None) -> None:
    """Run a single live-stack tick (testing)."""
    cfg = DaemonConfig.from_env_and_yaml()
    if traces_dir:
        cfg.traces_dir = traces_dir
    try:
        result = run_daemon_tick(shadow_mode=shadow, config=cfg)
    except RuntimeError as exc:
        console.print(f"[bold red]{exc}[/bold red]")
        raise SystemExit(1) from exc

    console.print(
        json.dumps(
            {
                "trace_id": result.trace_id,
                "trace_path": str(result.trace_path),
                "decision_outcome": result.decision_outcome,
                "contact_sent": result.contact_sent,
                "shadow": result.shadow,
                "message": result.message,
                "observations_count": result.observations_count,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
