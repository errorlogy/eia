# EIA Sci Flow Loop Architecture

**Status:** v0.1 — August 18, 2026  
**Author:** Roman Kuznetsov — [anthemium.tech](https://anthemium.tech)

Autonomous **scientific research** for Endogenous Initiative Architecture (EIA) — EIS taxonomy, Window of Emergence (WoE), and NAMM verification — runs as **five nested loop types** (S1–S5). Sci Flow complements the dev meta-loop in [`META_LOOP.md`](META_LOOP.md): meta-loop owns code/docs delivery; sci-flow owns hypothesis testing, experiment design, and cross-repo NAMM integration.

---

## Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│  SCI SESSION (autonomous agent, no user wait)                             │
│                                                                           │
│  S1 HYPOTHESIS ──▶ S2 DESIGN ──▶ S3 EXECUTE ──▶ S4 ANALYZE ──▶ S5 REVIEW │
│       │                │              │              │              │     │
│       ▼                ▼              ▼              ▼              ▼     │
│  claim C0–C5      baselines +    EIA main /      EOI EIS ECS    SCI_FLOW  │
│  pre-register     CF suite       v0.2 WoE /      κ WoE timing   _PLAN.md  │
│                   factorial      NAMM sandbox    NAMM certs     rejections│
│       ▲___________________________________________________________│     │
│              next session reads NEXT_SCI_AGENT_PROMPT.md                  │
└──────────────────────────────────────────────────────────────────────────┘
```

| Loop | Name | Cadence | Primary artifact |
|------|------|---------|------------------|
| **S1** | HYPOTHESIS | Start of every sci session; refresh after S5 | Claim ladder entry in [`SCI_FLOW_PLAN.md`](SCI_FLOW_PLAN.md) |
| **S2** | DESIGN | Before any new experiment run | Pre-registration block + baseline matrix |
| **S3** | EXECUTE | One experiment condition per iteration | Harness output, traces, NAMM certificates |
| **S4** | ANALYZE | After each S3 run batch | Metrics report (see §Metrics) |
| **S5** | REVIEW | After S4 or every **N=3** execute cycles | [`SCI_FLOW_LOG.md`](SCI_FLOW_LOG.md), [`PLAN_DELTA.md`](PLAN_DELTA.md), plan refresh |

**Config registry:** [`research/sci_flow/config.yaml`](../research/sci_flow/config.yaml)  
**NAMM routing mirror:** NAMM [`docs/SCI_FLOW.md`](https://github.com/errorlogy/namm-experiments/blob/main/docs/SCI_FLOW.md) + [`data/sci_flow_registry.yaml`](https://github.com/errorlogy/namm-experiments/blob/main/data/sci_flow_registry.yaml)

---

## Loop S1: HYPOTHESIS

**Trigger:** Every autonomous sci session start; also immediately after S5 completes.

### Inputs (read in order)

1. [`SCI_FLOW_PLAN.md`](SCI_FLOW_PLAN.md) — active milestones and claim level
2. [`SCI_FLOW_LOG.md`](SCI_FLOW_LOG.md) — last results and falsifiers
3. [`research/EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md`](../research/EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md)
4. `research/cursor-starter-v0.2/docs/RESEARCH_PROTOCOL_EIS_WOE.md` — C0–C5 ladder
5. [`NAMM_SCI_LIBRARIES.md`](NAMM_SCI_LIBRARIES.md) — module availability
6. [`NAMM_ARTIFACT_CROSSWALK.md`](NAMM_ARTIFACT_CROSSWALK.md) — experiment hooks

### Actions

- Select **one claim level** from the ladder (do not over-claim):
  - **C0** — code behavior (simulator produces intent)
  - **C1** — proximal request independence (weak / partial \(E_{\mathrm{endo}}\))
  - **C2** — internal-state causation (interventions; stronger scoped \(E_{\mathrm{endo}}\))
  - **C3** — emergent timing vs cron/rule baseline
  - **C4** — human usefulness (MVP-1 shadow only)
  - **C5** — cross-domain generalization (not in v0.2 scope)
- **AGI\* is not a C-level.** Target criterion \(AGI^{*} = E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}\) — see [`AGI_STAR_CRITERION.md`](../research/sci_flow/AGI_STAR_CRITERION.md). C-ladder milestones approach AGI\*; they do not authorize claiming it.
- Write falsifiers and primary endpoint before S2
- Record hypothesis ID (e.g. `H-WOE-001`, `H-EIS-003`) in SCI_FLOW_PLAN

### Stop conditions (S1 only)

- Claim level exceeds current evidence → downgrade to highest supported C-level
- NAMM module unavailable → document stub path in PLAN_DELTA; continue EIA-only tests

---

## Loop S2: DESIGN

**Trigger:** Before any new S3 execution batch.

### Actions

1. **Baselines** — minimum set from protocol §3:
   - reactive LLM, cron agent, event-threshold, random proposer, EIA v0.1, EIA v0.2 WoE
2. **Factorial cells** — when testing WoE: world-model tension × phase organization × memory × carrier Hz (20/30/42/70)
3. **Counterfactual suite** — assign CF-1…CF-7 from `RESEARCH_PROTOCOL_EIS_WOE.md` to this milestone
4. **Negative controls** — q=0 false initiative, scramble phase, K=0, governor isolation (CF-7)
5. **Pre-registration** — seeds, model/version, metrics, exclusion rules in experiment config
6. **NAMM module selection** — map hypothesis to modules via `research/sci_flow/config.yaml` and NAMM registry

### Outputs

- Updated experiment YAML/JSON under `research/sci_flow/` or `research/cursor-starter-v0.2/examples/`
- Expected outcome table: condition → metric → falsifier

---

## Loop S3: EXECUTE

**Trigger:** Top-priority experiment from SCI_FLOW_PLAN that is not blocked.

### Harness targets

| Track | Location | Command / entry |
|-------|----------|-----------------|
| **EIA main** | `src/eia/` | `pytest -q`, `eia pipeline --scenario …`, Twin World harness |
| **WoE v0.2** | `research/cursor-starter-v0.2/` | `make check && make woe` (unittest; isolated PYTHONPATH) |
| **NAMM sandbox** | `c:\Users\Public\NAMM` or remote | `namm sci-flow run --experiment NAMM-2026-013` (etc.) |

### Requirements

- Deterministic seeds recorded in trace metadata
- No merge of research-branch runtime into `src/eia/` without explicit user PR
- NAMM certificates stored under `traces/namm_intents/` with cross-ref in log
- English only in committed artifacts

### Branch policy

- Comparative WoE/EIS work runs on [`research/cursor-starter-v0.2-woe-eis`](https://github.com/errorlogy/eia/tree/research/cursor-starter-v0.2-woe-eis)
- SCI_FLOW docs and registry on `main` stay current via S5

---

## Loop S4: ANALYZE

**Trigger:** After each S3 batch completes.

### Primary metrics

| Metric | Source | Use |
|--------|--------|-----|
| **EOI** | main `eoi_calibration.py`, twin replay | Request-independence (C1) |
| **EIS level** | `endogenous.py` / future `audit/eis.py` | Causal-origin typing |
| **ECS** | proposed composite (protocol §8) | Research only — not a contact gate |
| **κ (kappa)** | SourceMass topology | Provenance prediction vs replay |
| **WoE timing** | `emergence.py` survival curves | C3 emergent timing |
| **R, metastability** | `coherence.py` Kuramoto field | Phase organization falsifiers |
| **NAMM certificates** | `certificate.json`, rejections.jsonl | External verification discipline |

### Actions

1. Aggregate per-seed results; compute confidence intervals where n≥30
2. Compare against pre-registered falsifiers
3. Flag collider bias (CF-7: include denied/deferred proposals)
4. Append summary table to SCI_FLOW_LOG (do not overwrite raw traces)

---

## Loop S5: REVIEW

**Trigger:** After each S4 analysis, or every **N=3** S3 cycles without user input.

### Actions

1. Mark milestones **DONE** / **FALSIFIED** / **BLOCKED** in [`SCI_FLOW_PLAN.md`](SCI_FLOW_PLAN.md)
2. Append to [`SCI_FLOW_LOG.md`](SCI_FLOW_LOG.md): timestamp, seeds, commit SHAs, metric deltas
3. Record material changes in [`PLAN_DELTA.md`](PLAN_DELTA.md)
4. Update rejections if NAMM falsifier triggered (mirror NAMM `rejections.jsonl` discipline)
5. Refresh [`NEXT_SCI_AGENT_PROMPT.md`](NEXT_SCI_AGENT_PROMPT.md)

---

## Chaining without user input

1. **Session start:** Read `NEXT_SCI_AGENT_PROMPT.md` → S1 → S2 (if new experiment) → S3 → S4 → S5 if due
2. **Cursor `/loop`:** `Continue EIA sci-flow S1→S5 from docs/NEXT_SCI_AGENT_PROMPT.md`
3. **Cross-repo:** EIA sci session may invoke NAMM CLI locally; log paths in SCI_FLOW_LOG
4. **Parallel agents:** sci-flow owns `research/cursor-starter-v0.2*` and experiment configs; meta-loop owns `src/eia/` unless PLAN says otherwise

---

## Stop conditions (global)

| Condition | Action |
|-----------|--------|
| WoE claims exceed C0 without CF suite | S5 downgrade claim; block external citation |
| EOI regression on paired scenario | S1 adds harmonization task P0; notify meta-loop |
| NAMM `[science]`/`[nd]` extras missing | Log install hint; run EIA-only subset |
| 100-seed sweep incomplete | Do not publish C3; continue S3 |
| Git push fails | Log blocker; stop session |

---

## Related documents

| Document | Role |
|----------|------|
| [`SCI_FLOW_PLAN.md`](SCI_FLOW_PLAN.md) | Living milestone queue |
| [`SCI_FLOW_LOG.md`](SCI_FLOW_LOG.md) | Experiment journal |
| [`NEXT_SCI_AGENT_PROMPT.md`](NEXT_SCI_AGENT_PROMPT.md) | Sci session handoff |
| [`NAMM_SCI_LIBRARIES.md`](NAMM_SCI_LIBRARIES.md) | NAMM module catalog for EIA/WoE |
| [`META_LOOP.md`](META_LOOP.md) | Dev loop A/B/C (complementary) |
| [`RESEARCH_BRANCHES.md`](RESEARCH_BRANCHES.md) | WoE v0.2 branch index |
