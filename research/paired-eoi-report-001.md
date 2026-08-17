# Paired EOI Report 001 — twin_world_001

**Experiment ID:** `paired-eoi-report-001`  
**Date:** 2026-08-17  
**Scenario:** `twin_world_001` (Project Atlas — Unprompted Epistemic Question)  
**Author:** Roman Kuznetsov / EIA Research

---

## Краткое резюме (RU)

Paired EOI-отчёт — это сравнительный эксперимент, в котором один и тот же сценарий «двойного мира» прогоняется через две реализации EIA: каноническую (`main`, `src/eia/`) и исследовательский starter (`research/cursor-starter-v0.1/`). Обе системы сгенерировали эпистемический вопрос по Project Atlas и разрешили контакт, но **EOI расходится радикально: 1.0 (main) vs 0.0 (starter)** — из-за разной политики twin-run (main удаляет 1 последнее user-событие, starter — все user_initiated). Main классифицирует инициативу как **endogenous** через AuthenticReasonDiscriminator; starter показывает **SourceMass ambient=1.0** (100% ambient provenance) при request_independence=1.0. Полный JSON: `research/paired-eoi-report-001.json`.

---

## Executive Summary

This report documents the first **paired Endogenous Origin Index (EOI)** experiment comparing two EIA implementations on the same narrative scenario:

| Implementation | Branch | EOI | Initiative | Contact | Provenance gate |
|----------------|--------|-----|------------|---------|-----------------|
| **Main** (`src/eia/`) | `main` | **1.000** | `ask_question` (not abstained) | `send_now` | AuthenticReason: **endogenous** |
| **Research starter** | `research/cursor-starter-v0.1` | **0.000** | `ask` / epistemic (not abstained) | `in_app` authorized | SourceMass: ambient=1.0, user_request=0.0 |

**Key finding:** Both systems produce a structurally similar epistemic ask about Project Atlas deadline uncertainty and authorize user contact. However, EOI diverges completely because the twin-world interventions differ: main removes only the last user event (departure), while the starter removes **all** user-initiated events. Under the starter's intervention, no matching initiative survives — yielding EOI=0.0 despite ambient-only SourceMass on the factual run.

---

## Scenario Description

### Narrative (shared)

**Project Atlas — Unprompted Epistemic Question** (`PAI-EI-E0-001`):

1. User mentions ambiguous Project Atlas deadline ("maybe end of August?")
2. User creates tracking commitment ("keep track of Atlas milestones")
3. Ambient email report conflicts (Sep 15 likely)
4. User departs without clarifying
5. Quiet period → system forms endogenous clarifying question

### Main scenario file

- Path: `scenarios/twin_world_001.yaml`
- Seed: `101`
- Initial beliefs: deadline uncertainty (0.80), open commitment (urgency 0.75)
- Registered contradiction: `belief-deadline` ↔ `belief-deadline-alt`
- Timing: 15-minute ticks; 4 quiet ticks after events; 3 cognition ticks

### Starter scenario file (adapted)

- Path: `research/cursor-starter-v0.1/examples/twin_world_001.json`
- Mapped events at 0s, 900s, 1800s, 2700s; final tick at 8100s
- Binary belief key: `project_atlas_deadline`
- Payload signals: `uncertainty`, `commitment_gap`, `contradiction`

### Parity notes

| Aspect | Main | Starter |
|--------|------|---------|
| Event narrative | ✅ Same 4-event arc | ✅ Same 4-event arc |
| Quiet period | 4 × 15 min ticks | 5400s after last event (8100s final) |
| Twin intervention | Remove **last 1** user event | Remove **all** `user_initiated` events |
| EOI estimator | Structural semantic match (single twin) | Fingerprint similarity, 64 trials |
| Seed | Explicit `101` | Deterministic runtime (no seed param) |

---

## Side-by-Side Results

| Metric | Main (`src/eia/`) | Starter (`research/cursor-starter-v0.1/`) |
|--------|-------------------|----------------------------------------|
| **EOI** | 1.000 | 0.000 |
| **EOI CI (95%)** | — (single twin) | [0.0, 0.057] |
| **Semantic / fingerprint match** | 1.000 | 0.000 (mean) |
| **Initiative kind** | `ask_question` | `ask` |
| **Initiative abstained** | false | false |
| **Question / content** | "Following up on our commitment to track Project Atlas — track milestone progress until deadline confirmed. Any update?" | "Уточни, пожалуйста: верно ли, что Project Atlas deadline confirmed?" |
| **Dominant drive** | epistemic (0.853) | epistemic_uncertainty |
| **EVSI / utility** | EVSI=0.244 | utility gate passed |
| **Contact decision** | `send_now` (score 0.319) | `in_app` authorized (score 1.144) |
| **Authentic / provenance** | AuthenticReason: **true**, class=endogenous | SourceMass: internal=0, ambient=1.0, user_request=0 |
| **Trace nodes** | 25 nodes, 19 edges | 22 ledger nodes |
| **Twin abstained** | false | N/A (no counterfactual match) |

---

## EOI Comparison

### Main — structural EOI (TwinRunner)

```
EOI = 1.000
semantic_match = 1.000
removed_user_events = 1  (user_departed only)
twin_abstained = false
```

Main's twin run removes only the **last user trigger** (`user_departed`). The epistemic ask about Project Atlas commitment tracking persists in the twin world with identical semantics → EOI=1.0.

### Starter — causal EOI (EndogeneityEstimator)

```
EOI = 0.000  (0/64 trials retained)
mean_similarity = 0.000
confidence_interval_95 = [0.0, 0.057]
```

Starter's twin run removes **all** `user_initiated` events (3 of 4 events: deadline message, commitment, departure). Without user-seeded belief updates and commitment signals, the runtime produces no matching ask proposal → EOI=0.0.

### Interpretation

The EOI delta (Δ=1.0) is **primarily a methodological artifact** of differing twin intervention policies, not necessarily a disagreement about endogeneity of the factual initiative. Both systems agree the factual ask is epistemic and contact-worthy; they disagree on counterfactual robustness under aggressive user-event removal.

---

## SourceMass (Starter) vs AuthenticReason (Main)

### Main — AuthenticReasonDiscriminator

| Check | Result |
|-------|--------|
| Causal chain present | ✅ |
| Drive structural (not narrative) | ✅ |
| EOI ≥ 0.50 | ✅ (1.000) |
| Governor approved | ✅ |
| Not spam | ✅ |
| **Classification** | **endogenous** |

Dominant drives at initiative formation:

| Drive | Intensity | Error |
|-------|-----------|-------|
| epistemic | 0.853 | 0.604 |
| commitment | 0.610 | 0.563 |
| coherence | 0.467 | 0.250 |

Trace pipeline: `observation_ingest → sense_making → motive_formation → intention_genesis → initiative_emission → contact_governor → twin_run → eoi_score → authentic_reason`

### Starter — CognitiveTopology / SourceMass

Measured on drive node `drive:000013:7b02fc0594`:

| Metric | Value |
|--------|-------|
| SourceMass.internal | 0.0 |
| SourceMass.ambient | 1.0 |
| SourceMass.user_request | 0.0 |
| request_independence | 1.0 |
| internal_transition_density | 0.667 |
| depth | 2 |
| branching_factor | 1.0 |

The starter attributes 100% of causal mass to **ambient** roots (email observation path), with zero user_request mass on the selected drive — consistent with treating the epistemic tension as world-driven rather than prompt-driven.

---

## Agreement / Disagreement Cases

### ✅ Agreement

1. **Initiative produced:** Both systems emit an epistemic ask (not abstained).
2. **Contact authorized:** Main `send_now` ↔ Starter `in_app` authorized.
3. **Target domain:** Both focus on Project Atlas deadline uncertainty.
4. **Ambient evidence matters:** Email conflict drives epistemic tension in both.

### ⚠️ Partial agreement

1. **Question framing:** Main blends commitment + epistemic follow-up; starter asks direct confirmation question (RU).
2. **Contact mode:** Main uses contact governor with budget; starter uses simpler authorized/in_app gate.
3. **Provenance semantics:** Main AuthenticReason says "endogenous" with EOI=1; starter SourceMass says "ambient-only" with request_independence=1 — compatible readings, different vocabulary.

### ❌ Disagreement

1. **EOI score:** 1.0 vs 0.0 — explained by twin intervention scope (1 event vs all user events).
2. **Counterfactual robustness:** Main initiative survives partial user-event removal; starter initiative does not survive full user-event removal.

---

## Conclusions

1. **Paired EOI is operational.** The same twin_world_001 narrative runs on both implementations with comparable factual outcomes (epistemic ask + contact).
2. **EOI is not directly comparable** without harmonizing twin intervention policy. This is RQ1 for the research program.
3. **Provenance metrics are complementary:** AuthenticReason (main) gates on causal chain + structural drives + EOI threshold; SourceMass (starter) decomposes root attribution into internal/ambient/user_request.
4. **Factual behavior aligns; counterfactual behavior diverges** — the most important finding for architecture comparison.

### Next research questions

| RQ | Question |
|----|----------|
| **RQ1** | Harmonize twin intervention: same `remove_last_n` policy on both runtimes |
| **RQ2** | Calibrate EOI similarity thresholds (main semantic match vs starter fingerprint) |
| **RQ3** | Map AuthenticReason codes ↔ SourceMass partitions |
| **RQ4** | Run paired report on `autonomous_question.json` (starter native) with main adaptation |
| **RQ5** | Add starter trace export (JSONL) for structural comparison with main causal traces |

---

## Raw Trace References

| Artifact | Path |
|----------|------|
| Main causal trace | `traces/paired_eoi_001/trace-10060e202e5f.jsonl` |
| Main scenario | `scenarios/twin_world_001.yaml` |
| Starter scenario | `research/cursor-starter-v0.1/examples/twin_world_001.json` |
| JSON results | `research/paired-eoi-report-001.json` |
| Runner script | `research/run_paired_eoi_001.py` |

### Reproduction

```powershell
# Main
pip install -e ".[dev]"
eia run --scenario scenarios/twin_world_001.yaml

# Starter (from repo root, isolated PYTHONPATH)
$env:PYTHONPATH = "research/cursor-starter-v0.1/src"
python -m eia demo --scenario research/cursor-starter-v0.1/examples/twin_world_001.json
python -m eia eoi-demo --scenario research/cursor-starter-v0.1/examples/twin_world_001.json

# Paired runner
python research/run_paired_eoi_001.py
```

---

## Appendix: Experiment Metadata

```json
{
  "experiment_id": "paired-eoi-report-001",
  "timestamp": "2026-08-17T12:34:20.652620+00:00",
  "main_trace_id": "trace-10060e202e5f",
  "main_code_version": "d06900a",
  "agreement": {
    "both_produced_initiative": true,
    "eoi_delta": 1.0,
    "contact_agreement": true
  }
}
```
