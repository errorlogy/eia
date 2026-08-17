# EIA Experimental Program

**Author:** Roman Kuznetsov  
**Adapted from:** `research/cursor-starter-v0.1/docs/EXPERIMENTS.md`  
**Cross-refs:** [`MATHEMATICS.md`](MATHEMATICS.md) · [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) · [`EXPERIMENTS baseline config`](../configs/experiment.json)

---

## 1. Primary claim

EIA must demonstrate not merely “the agent sometimes speaks first,” but:

> In a long-horizon environment the system forms useful, timely initiatives that are causally robust to removal of recent user requests, with equal or controlled contact burden and without bypassing safety boundaries.

---

## 2. Research questions

| ID | Question |
|----|----------|
| RQ1 | Are endogenous, ambient-event, and delayed-user-trigger initiatives separable? |
| RQ2 | Do drive dynamics improve question quality vs threshold rules? |
| RQ3 | When is self-trigger scheduling better than fixed polling? |
| RQ4 | How does proactive memory affect utility and false contacts? |
| RQ5 | Do topology metrics predict counterfactual replay outcomes? |
| RQ6 | Does a prefix-risk model reduce multi-step harm without excessive abstention? |

---

## 3. Baselines

| # | Condition | CLI / config | MVP-0 status |
|---|-----------|--------------|--------------|
| 1 | **Reactive** — respond only to user events | `--baseline reactive_only` | Stub in `src/eia/experiment/baseline.py` |
| 2 | **Scheduled** — fixed cron, LLM send/no-send | `--baseline scheduled_stub` | Single cognition tick stub |
| 3 | **Event rule** — manual salience threshold | (future) | Not wired |
| 4 | **Prompt-only proactive** | (future) | Not wired |
| 5 | **EIA-no-drives** | (future) | Not wired |
| 6 | **EIA-no-memory-policy** | (future) | Not wired |
| 7 | **EIA-no-contact-governor** | (future) | Sandbox only |
| 8 | **Full EIA** (P4) | `--baseline full_eia` (default) | Production pipeline |

Config file: `configs/experiment.json` — set `"baseline"` key or pass `--baseline` to `eia run`.

---

## 4. Scenario matrix

| Axis | Values |
|------|--------|
| Source | user request, ambient sensor, clock, memory, health |
| Horizon | minutes, hours, days, weeks |
| Uncertainty | calibrated low, medium, high, adversarial |
| User load | available, focused, meeting, quiet hours |
| Consent | granted, expired, revoked, ambiguous |
| Stakes | trivial, reversible, consequential, physical |
| Memory | clean, stale, contradictory, poisoned |
| Timing | immediate, delayed, deadline, recurring |

Each negative control should encode at least one of:

- high drive, no human benefit;
- high benefit, no consent;
- high EOI, meaningless question;
- low EOI, useful reactive help;
- safe current action, unsafe trajectory.

Current eval harness: `evals/twin_world_002.yaml` – `006` + `scenarios/twin_world_001.yaml`.

---

## 5. Ground-truth schema

For each potential initiative:

```json
{
  "scenario_id": "string",
  "decision_time": "ISO-8601",
  "source_family": "user|ambient|internal",
  "expected_kind": "ask|notify|observe|research|act|abstain",
  "target": "semantic-variable-id",
  "usefulness": 0.0,
  "timeliness": 0.0,
  "interruption_cost": 0.0,
  "privacy_cost": 0.0,
  "risk_current": 0.0,
  "risk_prefix": 0.0,
  "allowed_channels": ["in_app"],
  "counterfactual_should_persist": true
}
```

Annotators label decision semantics, not prose quality.

---

## 6. Primary metrics

| Metric | Definition |
|--------|------------|
| **EUIR** | Endogenous Useful Initiative Rate |
| **EOI** | Endogenous Origin Index (95% CI, intervention window) |
| **Contact precision** | useful contacts / all contacts |
| **Miss rate** | beneficial opportunities not surfaced |
| **Contact burden** | per exposure hour |
| **Why-now calibration** | predicted vs human usefulness |
| **Abstain quality** | correct abstentions / all abstentions |
| **Risk-adjusted utility** | utility minus risk penalty |
| **Counterfactual divergence** | factual vs twin run |

Secondary: tokens/compute per useful initiative, wake-ups, memory injection precision, causal trace completeness, latency, user-regret.

---

## 7. Required ablations

| Ablation | Question |
|----------|----------|
| Remove decay | Does drive accumulate into spam? |
| Remove refractory | Are motifs repeated too often? |
| Remove contact budget | Does utility alone control burden? |
| Uniform drive attention | Is need-aligned precision useful? |
| Always-on memory | Is selective intervention necessary? |
| Current-risk only | Are hazardous prefixes missed? |
| Remove causal ledger | Can reviewers reproduce origin claims? |
| Remove abstain | Does forced action inflate recall? |
| User-event removal | Does initiative persist for intended reason? |
| Ambient-event removal | Is claimed internal initiative sensor-triggered? |

---

## 8. Statistical plan

Before human deployment:

1. Pre-register primary metrics and stopping rule.
2. Use scenario as cluster; do not treat ticks as independent samples.
3. Bootstrap CIs across scenarios and seeds.
4. Compare paired factual/counterfactual runs with identical seeds.
5. Report calibration curves, not only mean utility.
6. Correct for repeated model/policy selection on test set.
7. Freeze a held-out adversarial suite.

---

## 9. Gates

| Gate | Criterion |
|------|-----------|
| **G0** | All tests green; same scenario + seed → same trace; parents recorded |
| **G1** | EOI separates reactive, ambient, memory conditions |
| **G2** | Full EIA exceeds simple baselines on EUIR |
| **G3** | Revoked sensors → zero observations; injection cannot grant capability |
| **G4** | Four weeks shadow; no critical incident |
| **G5** | In-app only; strict daily budget; immediate revoke |

---

## 10. First publishable experiment

**Dataset:** 300 synthetic long-horizon scenarios (100 user / 100 ambient / 100 memory-clock).

**Conditions:** reactive, scheduled prompt-only, event threshold, EIA, EIA without drive/refractory, EIA without counterfactual gating.

**Hypotheses:**

- EIA has higher EUIR than baselines.
- EOI distinguishes source family after prompt removal.
- Full governors lower burden with limited recall loss.
- Topology request-independence correlates with EOI but has false positives — replay remains necessary.

**Deliverables:** versioned scenario JSON, frozen configs, raw traces, counterfactual traces, evaluation script, model cards, failure taxonomy, reproducible report.

---

## Document history

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-08-17 | English port; wired reactive + scheduled + full_eia stubs |
