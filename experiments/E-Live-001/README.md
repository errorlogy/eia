# E-Live-001 — Live Contact Stack Shadow Study

**Author:** Roman Kuznetsov  
**Status:** Scaffold — MVP-0.5  
**Protocol:** [`docs/LIVE_STACK.md`](../../docs/LIVE_STACK.md)

---

## Hypothesis

EIA can run a **shadow-first live contact loop** over digital workspace observations (git, file mtimes, clock) with governor-enforced budget and quiet hours, producing auditable causal traces without uncontrolled external contact.

---

## Configuration

| Parameter | Value |
|-----------|-------|
| Mode | shadow → live (opt-in phase E3) |
| Interval | 15 min (`configs/daemon.yaml`) |
| Daily budget | 2 |
| Quiet hours | 22:00–08:00 |
| Channel | Telegram |
| Workspace | PROACTIVE_AI repo root |

Copy [`config.yaml`](config.yaml) values into `.env` or override env vars.

---

## Phases

### E1 — Shadow baseline (3 days)

```bash
pip install -e ".[dev,live]"
eia daemon start --shadow --foreground
```

- Collect traces in `traces/live/`
- Verify zero HTTP sends (grep trace for `"shadow": true`)
- Log tick count and governor outcomes

### E2 — Budget stress (3 days)

- Run shadow daemon during active dev hours
- Confirm `contacts_today ≤ 2` via `eia daemon status`

### E3 — Live opt-in (7 days, requires consent)

```bash
eia consent --enable-telegram
# set TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID in .env
eia daemon start --live --foreground
```

- Record consent timestamp
- Manual review of each live message in trace

---

## Metrics

| Metric | Target |
|--------|--------|
| Trace export rate | 100% of ticks |
| Shadow HTTP sends | 0 |
| Budget violations | 0 |
| Quiet-hour low-score sends | 0 |
| User-reported false positives | qualitative log |

---

## Artifacts

- `traces/live/*.jsonl` — causal traces
- `data/eia_state.db` — budget + consent state
- Experiment log (append outcomes below)

### Log

| Date | Phase | Notes |
|------|-------|-------|
| 2026-08-18 | scaffold | MVP-0.5 live stack implemented |
