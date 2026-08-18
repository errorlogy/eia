# EIA Live Stack (MVP-0.5)

**Author:** Roman Kuznetsov  
**Status:** MVP-0.5 — shadow-first live contact via Telegram  
**Experiment:** E-Live-001

---

## Overview

The live stack extends EIA from scenario-based simulation to **proactive contact** in a real workspace. Default mode is **shadow**: full cognitive pipeline + causal trace + governor, but Telegram messages are logged to stdout and trace only — no HTTP send.

| Component | Path | Role |
|-----------|------|------|
| State store | `src/eia/runtime/state_store.py` | SQLite budget, consent, quiet hours |
| Digital observations | `src/eia/observations/digital.py` | Git log, file mtimes, clock |
| Telegram adapter | `src/eia/contact/telegram_adapter.py` | Bot API send / shadow log |
| Daemon runtime | `src/eia/runtime/daemon.py` | APScheduler tick every 15 min |
| Config | `configs/daemon.yaml` | Interval, budget, quiet hours |

---

## Safety defaults

- **Shadow mode** is default (`eia daemon start --shadow`, `eia tick`)
- **Max 2 contacts/day** (`CONTACT_DAILY_BUDGET` / state store)
- **Quiet hours** 22:00–08:00 UTC (configurable via `EIA_QUIET_HOURS=22-8`)
- **Live mode** requires explicit consent + env vars

---

## Setup

### 1. Install with live extras

```bash
pip install -e ".[dev,live]"
```

Core install (`pip install -e .`) works without live deps; daemon scheduler requires `[live]`.

### 2. Configure environment

Copy `.env.example` → `.env` and set:

```env
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=your_chat_id
EIA_DAEMON_INTERVAL_MIN=15
EIA_QUIET_HOURS=22-8
EIA_WORKSPACE=c:\Users\Public\PROACTIVE_AI
CONTACT_DAILY_BUDGET=2
```

**Get Telegram credentials:**

1. Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy token
2. Start chat with your bot, send any message
3. Open `https://api.telegram.org/bot<TOKEN>/getUpdates` → find `"chat":{"id":...}`

### 3. Shadow mode (recommended first)

```bash
# Single tick — inspect trace
eia tick --shadow

# Background daemon (15 min interval)
eia daemon start --shadow --foreground
```

Traces land in `traces/live/`. Shadow output appears as `[EIA shadow contact] {...}` on stdout.

### 4. Enable live Telegram

```bash
eia consent --enable-telegram
eia tick --live          # one test send
eia daemon start --live --foreground
```

Live mode fails fast if consent or env vars are missing.

### 5. Status

```bash
eia daemon status
eia consent              # show consent + budget snapshot
```

---

## Experiment E-Live-001 protocol

See [`experiments/E-Live-001/README.md`](../experiments/E-Live-001/README.md).

| Phase | Duration | Mode | Success criteria |
|-------|----------|------|------------------|
| E1 | 3 days | shadow | ≥1 trace/tick, 0 HTTP sends, governor DEFER/SEND logged |
| E2 | 3 days | shadow + budget stress | contacts_today never exceeds 2 |
| E3 | 7 days | live (opt-in) | ≤2 contacts/day, no quiet-hour sends unless score ≥0.7 |

Record traces under `traces/live/` and note consent timestamp in experiment log.

---

## Architecture

```
APScheduler (15 min)
    │
    ▼
collect_digital_observations()
    │
    ▼
CognitiveLoop: ingest → sense → motive → intention → governor
    │
    ▼
SEND_NOW? ──shadow──► log stdout + trace
         └──live───► Telegram Bot API (if consent)
    │
    ▼
StateStore.record_contact() + trace JSONL export
```

---

## CLI reference

| Command | Description |
|---------|-------------|
| `eia tick [--shadow\|--live]` | Single manual tick |
| `eia daemon start [--shadow\|--live] [--foreground]` | Start scheduler |
| `eia daemon status` | PID, budget, consent |
| `eia consent --enable-telegram` | Grant live contact consent |

---

## Related docs

- [`MVP1_SHADOW_PLAN.md`](MVP1_SHADOW_PLAN.md) — prior shadow planning
- [`LOOP_PLAN.md`](LOOP_PLAN.md) — iteration roadmap
- [`THREAT_MODEL.md`](THREAT_MODEL.md) — adversarial governor cases
