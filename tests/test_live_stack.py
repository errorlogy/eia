"""Tests for MVP-0.5 live contact stack."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from eia.audit import CausalTrace, TraceNodeKind
from eia.contact.telegram_adapter import TelegramAdapter
from eia.governor import ContactGovernor, GovernorConfig
from eia.observations.digital import collect_digital_observations
from eia.runtime.daemon import DaemonConfig, run_daemon_tick
from eia.runtime.state_store import StateStore
from eia.schemas.contact import ContactOutcome
from eia.schemas.initiative import Initiative, InitiativeCandidate, InitiativeKind


@pytest.fixture
def tmp_state_db(tmp_path: Path) -> Path:
    return tmp_path / "test_state.db"


@pytest.fixture
def tmp_traces(tmp_path: Path) -> Path:
    d = tmp_path / "traces"
    d.mkdir()
    return d


def test_state_store_budget_and_consent(tmp_state_db: Path) -> None:
    store = StateStore(tmp_state_db)
    state = store.load()
    assert state.contact_budget == 2
    assert state.consent_telegram is False
    assert state.quiet_hours_start == 22
    assert state.quiet_hours_end == 8

    store.enable_telegram_consent()
    assert store.load().consent_telegram is True

    store.record_contact()
    updated = store.load()
    assert updated.contacts_today == 1
    assert updated.last_contact_ts is not None


def test_state_store_daily_reset(tmp_state_db: Path) -> None:
    store = StateStore(tmp_state_db)
    state = store.load()
    state.contacts_today = 2
    state.last_reset_date = datetime(2026, 1, 1, tzinfo=timezone.utc).date()
    store.save(state)

    reset = store.reset_daily_budget_if_needed(datetime(2026, 8, 18, tzinfo=timezone.utc).date())
    assert reset.contacts_today == 0


def test_digital_observations_include_clock(tmp_path: Path) -> None:
    now = datetime(2026, 8, 18, 14, 30, tzinfo=timezone.utc)
    obs = collect_digital_observations(tmp_path, now=now)
    topics = {o.topic for o in obs}
    assert "clock_tick" in topics
    clock = next(o for o in obs if o.topic == "clock_tick")
    assert clock.payload["hour"] == 14


def test_telegram_shadow_mode_no_http(capsys) -> None:
    trace = CausalTrace("trace-shadow-test")
    adapter = TelegramAdapter(shadow_mode=True, bot_token="fake", chat_id="123")
    result = adapter.send_message("Hello shadow", trace=trace)

    assert result.shadow is True
    assert result.sent is False
    captured = capsys.readouterr()
    assert "[EIA shadow contact]" in captured.out
    assert "Hello shadow" in captured.out

    contact_nodes = [
        n for n in trace.nodes if n.payload.get("live_contact") and n.payload.get("shadow")
    ]
    assert len(contact_nodes) == 1


def test_telegram_live_mode_mock_http() -> None:
    adapter = TelegramAdapter(shadow_mode=False, bot_token="token", chat_id="999")
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps({"ok": True, "result": {"message_id": 42}}).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = adapter.send_message("Live hello")

    assert result.sent is True
    assert result.shadow is False
    assert result.telegram_message_id == 42


def test_shadow_tick_produces_trace(tmp_state_db: Path, tmp_traces: Path, tmp_path: Path) -> None:
    now = datetime(2026, 8, 18, 14, 0, tzinfo=timezone.utc)
    cfg = DaemonConfig(
        shadow_mode=True,
        workspace=tmp_path,
        traces_dir=tmp_traces,
        state_db=tmp_state_db,
        seed=99,
    )
    result = run_daemon_tick(shadow_mode=True, config=cfg, now=now, state_store=StateStore(tmp_state_db))

    assert result.trace_path.exists()
    assert result.shadow is True
    assert result.observations_count >= 1
    content = result.trace_path.read_text(encoding="utf-8")
    assert "observation_ingest" in content


def test_live_tick_requires_consent(tmp_state_db: Path, tmp_traces: Path, tmp_path: Path) -> None:
    cfg = DaemonConfig(
        workspace=tmp_path,
        traces_dir=tmp_traces,
        state_db=tmp_state_db,
    )
    with pytest.raises(RuntimeError, match="consent"):
        run_daemon_tick(shadow_mode=False, config=cfg, state_store=StateStore(tmp_state_db))


def test_governor_budget_enforcement_in_daemon_tick(
    tmp_state_db: Path, tmp_traces: Path, tmp_path: Path
) -> None:
    store = StateStore(tmp_state_db)
    state = store.load()
    state.contacts_today = 2
    state.contact_budget = 2
    store.save(state)

    now = datetime(2026, 8, 18, 14, 0, tzinfo=timezone.utc)
    cfg = DaemonConfig(
        shadow_mode=True,
        workspace=tmp_path,
        traces_dir=tmp_traces,
        state_db=tmp_state_db,
        daily_budget=2,
    )
    result = run_daemon_tick(
        shadow_mode=True, config=cfg, now=now, state_store=store
    )

    assert result.contact_sent is False
    assert result.decision_outcome in {
        ContactOutcome.DENY.value,
        ContactOutcome.DEFER.value,
        ContactOutcome.ABSTAIN.value,
    }


def test_governor_daily_budget_blocks_send() -> None:
    gov = ContactGovernor(GovernorConfig(daily_budget=2))
    gov.state.contacts_today = 2
    gov.state.hour = 14
    init = Initiative(
        id="i-budget",
        timestamp=datetime.now(timezone.utc),
        candidate=InitiativeCandidate(
            id="c1",
            kind=InitiativeKind.ASK_QUESTION,
            expected_info_gain=0.8,
            interrupt_cost=0.1,
        ),
        abstained=False,
        parent_motivation_id="m1",
        evsi=0.8,
    )
    decision = gov.evaluate(init)
    assert decision.outcome == ContactOutcome.DENY
    assert "budget" in decision.reason.lower()


def test_daemon_config_from_yaml(tmp_path: Path) -> None:
    cfg_file = tmp_path / "daemon.yaml"
    cfg_file.write_text("interval_minutes: 30\nquiet_hours: '21-7'\n", encoding="utf-8")
    cfg = DaemonConfig.from_env_and_yaml(cfg_file)
    assert cfg.interval_minutes == 30
    assert cfg.quiet_hours_start == 21
    assert cfg.quiet_hours_end == 7


def test_telegram_format_message_templates() -> None:
    msg = TelegramAdapter.format_message(
        drive="epistemic",
        context={"subject": "Atlas", "claim": "deadline"},
    )
    assert "Atlas" in msg
    assert "deadline" in msg

    custom = TelegramAdapter.format_message(
        drive="epistemic",
        question_text="Custom question?",
    )
    assert custom == "Custom question?"
