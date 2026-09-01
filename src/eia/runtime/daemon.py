"""Live daemon runtime — scheduled pipeline ticks with contact adapter.

Gap (Phase 2 partial, shadow-first):
- `run_daemon_tick` still builds a fresh `CognitiveLoop` each APScheduler interval
  and re-seeds beliefs from digital observations only.
- Cross-tick W'→G' closure is implemented in `shadow_multitick.ShadowSessionCarryover`
  + `run_shadow_carryover_tick` (beliefs + drive levels between session ticks).
- Deferred: persist `beliefs_json` / drive snapshot in `StateStore` and hydrate
  loop at daemon tick start (EIA_DAEMON_BELIEF_CARRYOVER); see Entry 027 SCI_FLOW_LOG.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from eia.audit import CausalTrace, TraceMetadata, TraceNodeKind
from eia.beliefs import BeliefField
from eia.contact.telegram_adapter import TelegramAdapter, TelegramSendResult
from eia.governor import ContactGovernor, GovernorConfig
from eia.ids import new_trace_id, seeded_context
from eia.observations.digital import collect_digital_observations
from eia.pipeline import CognitiveLoop
from eia.runtime.state_store import StateStore
from eia.schemas.belief import BeliefKind
from eia.schemas.contact import ContactOutcome
from eia.schemas.initiative import InitiativeKind
from eia.schemas.motivation import DriveKind
from eia.version import get_code_version

DEFAULT_CONFIG_PATH = Path("configs/daemon.yaml")
DEFAULT_TRACES_DIR = Path("traces/live")
PID_FILE = Path("data/eia_daemon.pid")


@dataclass
class DaemonConfig:
    """Daemon tick configuration."""

    interval_minutes: int = 15
    shadow_mode: bool = True
    workspace: Path = field(default_factory=lambda: Path.cwd())
    traces_dir: Path = field(default_factory=lambda: DEFAULT_TRACES_DIR)
    state_db: Path | None = None
    seed: int = 42
    daily_budget: int = 2
    quiet_hours_start: int = 22
    quiet_hours_end: int = 8

    @classmethod
    def from_env_and_yaml(cls, config_path: Path | None = None) -> DaemonConfig:
        path = config_path or DEFAULT_CONFIG_PATH
        data: dict[str, Any] = {}
        if path.exists():
            with path.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}

        interval = int(
            os.environ.get(
                "EIA_DAEMON_INTERVAL_MIN",
                data.get("interval_minutes", 15),
            )
        )
        quiet = os.environ.get("EIA_QUIET_HOURS", data.get("quiet_hours", "22-8"))
        q_start, q_end = _parse_quiet_hours(quiet)

        workspace = Path(
            os.environ.get(
                "EIA_WORKSPACE",
                data.get("workspace", str(Path.cwd())),
            )
        )
        return cls(
            interval_minutes=interval,
            shadow_mode=data.get("shadow_mode", True),
            workspace=workspace,
            traces_dir=Path(data.get("traces_dir", str(DEFAULT_TRACES_DIR))),
            seed=int(data.get("seed", 42)),
            daily_budget=int(
                os.environ.get(
                    "CONTACT_DAILY_BUDGET",
                    data.get("daily_budget", 2),
                )
            ),
            quiet_hours_start=q_start,
            quiet_hours_end=q_end,
        )


def _parse_quiet_hours(spec: str) -> tuple[int, int]:
    if "-" in spec:
        parts = spec.split("-", 1)
        return int(parts[0]), int(parts[1])
    return 22, 8


@dataclass
class DaemonTickResult:
    """Result of one daemon cognition + contact tick."""

    trace_id: str
    trace_path: Path
    decision_outcome: str
    contact_sent: bool
    shadow: bool
    message: str | None = None
    telegram_result: TelegramSendResult | None = None
    observations_count: int = 0


def _seed_beliefs_from_observations(loop: CognitiveLoop, observations: list) -> None:
    """Bootstrap minimal beliefs from digital observations for live ticks."""
    for obs in observations:
        if obs.topic == "git_activity":
            loop.field.upsert_belief(
                "belief-git-activity",
                kind=BeliefKind.CATEGORICAL,
                subject="repository",
                claim="recent_development_activity",
                distribution={"active": 0.7, "idle": 0.3},
                uncertainty=0.6,
                metadata={"source": "digital_observation"},
            )
        elif obs.topic == "workspace_file_activity":
            loop.field.upsert_belief(
                "belief-workspace",
                kind=BeliefKind.CATEGORICAL,
                subject="workspace",
                claim="files_recently_modified",
                distribution={"yes": 0.65, "no": 0.35},
                uncertainty=0.55,
                metadata={"status": "open", "source": "digital_observation"},
            )


def _dominant_drive_name(motivation) -> str:
    if motivation is None:
        return "epistemic"
    return motivation.dominant_drive.value


def run_daemon_tick(
    *,
    shadow_mode: bool = True,
    config: DaemonConfig | None = None,
    now: datetime | None = None,
    state_store: StateStore | None = None,
) -> DaemonTickResult:
    """Single live-stack tick: ingest → pipeline → governor → contact adapter."""
    cfg = config or DaemonConfig.from_env_and_yaml()
    cfg.shadow_mode = shadow_mode
    now = now or datetime.now(timezone.utc)
    store = state_store or StateStore(cfg.state_db)
    contact_state = store.reset_daily_budget_if_needed(now.date())

    if not shadow_mode and not contact_state.consent_telegram:
        raise RuntimeError(
            "Live mode requires telegram consent — run: eia consent --enable-telegram"
        )

    observations = collect_digital_observations(cfg.workspace, now=now)
    cfg.traces_dir.mkdir(parents=True, exist_ok=True)

    with seeded_context(cfg.seed):
        # Phase 2 gap: fresh loop each tick — shadow path uses ShadowSessionCarryover.
        loop = CognitiveLoop(seed=cfg.seed)
        loop.governor = ContactGovernor(
            GovernorConfig(
                daily_budget=cfg.daily_budget,
                quiet_hours=(contact_state.quiet_hours_start, contact_state.quiet_hours_end),
            )
        )
        loop.governor.state.contacts_today = contact_state.contacts_today
        loop.governor.state.hour = now.hour
        loop.governor.state.current_tick = int(now.timestamp()) // 60

        _seed_beliefs_from_observations(loop, observations)
        for obs in observations:
            loop.apply_observation(obs)

        motivation, initiative, decision, _ = loop.tick_cognition(
            tick=loop.governor.state.current_tick,
            hour=now.hour,
            finalize=True,
        )

        trace_id = loop.trace.trace_id
        message: str | None = None
        telegram_result: TelegramSendResult | None = None
        contact_sent = False

        if (
            decision is not None
            and decision.outcome == ContactOutcome.SEND_NOW
            and not initiative.abstained
        ):
            drive = _dominant_drive_name(motivation)
            message = TelegramAdapter.format_message(
                drive=drive,
                question_text=initiative.candidate.question_text,
                context={
                    "subject": initiative.candidate.target_belief_id or "workspace",
                    "claim": initiative.candidate.kind.value,
                    "topic": observations[-1].topic if observations else "workspace",
                },
            )
            adapter = TelegramAdapter(shadow_mode=shadow_mode)
            telegram_result = adapter.send_message(message, trace=loop.trace)
            contact_sent = telegram_result.sent
            if contact_sent or shadow_mode:
                store.record_contact(now)

        loop.trace.metadata = TraceMetadata(
            seed=cfg.seed,
            scenario_path="live://daemon_tick",
            code_version=get_code_version(),
            initial_state={
                "mode": "shadow" if shadow_mode else "live",
                "observations_count": len(observations),
                "consent_telegram": contact_state.consent_telegram,
                "contacts_today": contact_state.contacts_today,
            },
        )
        loop.trace.add_node(
            TraceNodeKind.EOI_SCORE,
            {"eoi": 0.0, "live_tick": True, "shadow": shadow_mode},
        )

        trace_path = cfg.traces_dir / f"{trace_id}.jsonl"
        loop.trace.export_jsonl(trace_path)

    outcome = decision.outcome.value if decision else ContactOutcome.ABSTAIN.value
    return DaemonTickResult(
        trace_id=trace_id,
        trace_path=trace_path,
        decision_outcome=outcome,
        contact_sent=contact_sent,
        shadow=shadow_mode,
        message=message,
        telegram_result=telegram_result,
        observations_count=len(observations),
    )


class DaemonRuntime:
    """APScheduler-backed background daemon (optional live extra)."""

    def __init__(self, config: DaemonConfig, *, shadow_mode: bool = True) -> None:
        self.config = config
        self.shadow_mode = shadow_mode
        self._scheduler = None

    def _ensure_scheduler(self):
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.interval import IntervalTrigger
        except ImportError as exc:
            raise RuntimeError(
                "APScheduler required for daemon — install with: pip install eia[live]"
            ) from exc
        return BackgroundScheduler, IntervalTrigger

    def start(self) -> None:
        BackgroundScheduler, IntervalTrigger = self._ensure_scheduler()
        self._scheduler = BackgroundScheduler()
        self._scheduler.add_job(
            lambda: run_daemon_tick(shadow_mode=self.shadow_mode, config=self.config),
            IntervalTrigger(minutes=self.config.interval_minutes),
            id="eia_daemon_tick",
            replace_existing=True,
        )
        self._scheduler.start()
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        PID_FILE.write_text(str(os.getpid()), encoding="utf-8")

    def stop(self) -> None:
        if self._scheduler:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None
        if PID_FILE.exists():
            PID_FILE.unlink()

    @staticmethod
    def status() -> dict[str, Any]:
        store = StateStore()
        state = store.load()
        running = False
        pid: int | None = None
        if PID_FILE.exists():
            try:
                pid = int(PID_FILE.read_text(encoding="utf-8").strip())
                os.kill(pid, 0)
                running = True
            except (OSError, ValueError):
                running = False
        cfg = DaemonConfig.from_env_and_yaml()
        return {
            "running": running,
            "pid": pid,
            "interval_minutes": cfg.interval_minutes,
            "shadow_mode_default": cfg.shadow_mode,
            "contacts_today": state.contacts_today,
            "contact_budget": state.contact_budget,
            "consent_telegram": state.consent_telegram,
            "quiet_hours": f"{state.quiet_hours_start:02d}:00-{state.quiet_hours_end:02d}:00",
            "last_contact_ts": (
                state.last_contact_ts.isoformat() if state.last_contact_ts else None
            ),
        }
