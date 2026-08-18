# MVP-1 Shadow Mode Plan (Skeleton)

**Status:** Planning — shadow mode only (no live sensors)  
**Author:** Roman Kuznetsov  
**Date:** 2026-08-17  
**Parent:** [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) MVP-1 · [`PLAN_DELTA.md`](PLAN_DELTA.md)

---

## Goal

Deploy EIA pipeline in **shadow mode**: full cognitive loop + causal trace + governors, but **no external contact emission**. Observations from recorded streams only; consent and sensor fabric stubbed.

---

## Scope (MVP-1 shadow)

| Component | Shadow behavior | Live deferred |
|-----------|-----------------|---------------|
| Observation ingest | Recorded / synthetic YAML scenarios | L2–L4 sensor drivers |
| SenseMaking | BeliefField + NAMM hooks (006, 004) | Real-time multimodal |
| DriveEngine | Structural drives from beliefs | Wearable / ambient feeds |
| Contact Governor | Evaluate + log decisions; **force DEFER** in shadow | External messaging |
| Twin / EOI | Full counterfactual replay | — |
| AuthenticReason | Full verdict + optional NAMM cert | — |
| Consent UI | Stub spec below | Production consent flow |

---

## Sensors deferred checklist

- [ ] Camera / audio driver interface (`SensorHarness` contract)
- [ ] Consent scope registry (per-sensor TTL)
- [ ] Event backbone (NATS JetStream) — MVP-1 platform
- [ ] Clock sync for multimodal alignment
- [ ] Fault injection harness (drop, delay, corrupt)
- [ ] pgvector memory store for episodic recall
- [ ] OpenTelemetry export from pipeline stages
- [ ] Human-in-the-loop escalation on shadow anomalies

---

## Consent UI stub spec

**Purpose:** Record consent state transitions without blocking shadow runs.

```yaml
consent_stub:
  version: "0.1"
  default_scope: shadow_recorded_only
  states:
    - granted: { sensors: [synthetic_yaml], ttl_hours: 24 }
    - revoked: { sensors: [], effective: immediate }
  ui_placeholder:
    component: ConsentBannerStub
    actions: [grant_shadow, revoke_all]
    persistence: traces/consent/consent-{session_id}.json
```

**Acceptance:** Shadow runs write consent snapshot to trace metadata; governor reads stub and never emits SEND_NOW when `default_scope=shadow_recorded_only`.

---

## Entry criteria (from MVP-0)

- [x] G2 gate PASS ([`research/G2_EVIDENCE_PACK.md`](../research/G2_EVIDENCE_PACK.md))
- [x] Deterministic replay + CI ([`.github/workflows/eia-ci.yml`](../.github/workflows/eia-ci.yml))
- [x] 5-baseline matrix on eval set (PAI-EI-E0-001)
- [ ] Shadow flag in `run_scenario` / CLI
- [ ] Recorded-stream fixture pack (E1 replay)

---

## Exit criteria (MVP-1 shadow)

1. ≥10 recorded scenarios with full trace + EOI ≥ 0.5 on endogenous cases
2. Shadow governor: 0 external contacts in 100 shadow runs
3. Consent stub transitions logged on revoke mid-run (extends ADV-005–007 pattern)
4. NAMM-013 certificate wired in AuthenticReason when sandbox available

---

## Task queue (shadow mode)

| # | Task | Track | Depends |
|---|------|-------|---------|
| 1 | `--shadow` CLI flag + governor DEFER override | code | — |
| 2 | Consent stub loader + trace metadata | code | 1 |
| 3 | Recorded stream scenario pack (E1) | research | 1 |
| 4 | Shadow run batch + metrics dashboard stub | research | 2, 3 |
| 5 | MVP-1 platform spike (NATS + Postgres schema) | platform | 4 |

---

## Document history

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-08-17 | Initial skeleton — Loop 26 |
