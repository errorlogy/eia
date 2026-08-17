# Research Agenda: Cursor Starter v0.1

**Branch:** `research/cursor-starter-v0.1`  
**Date:** 2026-08-17  
**Author:** Roman Kuznetsov

This document records why the ChatGPT Cursor Research Starter lives on an isolated branch and what concrete investigations it enables against the canonical EIA implementation on `main`.

---

## Conclusion: Why Keep This as a Separate Branch

### 1. Parallel implementation hypothesis

The starter and `main` pursue the same scientific claim — *useful, timely initiatives whose nearest sufficient cause is not a recent user prompt* — but encode it in **incompatible architectural commitments**:

- **Starter:** single event-sourced cognitive loop (`runtime.py`), proposals compete inside one process, LLM has no direct contact path.
- **Main:** explicit five-stage pipeline (`CognitiveLoop` in `src/eia/pipeline.py`) with labeled stage traces, NAMM hooks, and `AgentState` schema.

Keeping both implementations side-by-side without merging allows **controlled A/B comparison** on identical Twin World scenarios. Merging would collapse two falsifiable hypotheses into one untestable hybrid.

### 2. Comparative evaluation: starter runtime vs main five-stage pipeline

| Dimension | Starter | Main |
|-----------|---------|------|
| Orchestration | Monolithic runtime tick | Stage-separated loop with `PipelineStageResult` |
| Trace granularity | Causal ledger + topology paths | `CausalTrace` + stage payloads + replay metadata |
| Abstention | Policy scoring + governors | `IntentionGenesis` EVSI threshold + governor |
| Test surface | 15 unit/integration tests in starter | Growing harness around pipeline + audit |

**Research value:** run the same JSON scenario on both branches and compare EUIR, contact precision, EOI distributions, and trace interpretability. Disagreement between branches is itself a signal about which decomposition better supports falsification.

### 3. Unique assets in this package

Assets worth preserving on this branch even if never ported wholesale to `main`:

1. **Cognitive topology / SourceMass** (`topology.py`, `causal.py`) — decomposes initiative provenance into `internal`, `ambient`, and `user_request` mass with `request_independence` and graph metrics (depth, branching). Main uses `AuthenticReasonDiscriminator` with structural vs narrative drive checks; the two approaches answer the same RQ1 with different operationalizations.

2. **Threat model** (`docs/THREAT_MODEL.md`) — explicit assets, trust boundaries, and abuse cases (prompt injection, memory poisoning, engagement hacking, bystander leakage). Main has governor gates but no consolidated adversarial catalog; this doc seeds a **ContactGovernor adversarial harness**.

3. **Experiment program RQ1–RQ6** (`docs/EXPERIMENTS.md`) — eight baselines, scenario matrix, ground-truth schema, primary metrics (EUIR, EOI, contact precision). Main's `IMPLEMENTATION_PLAN.md` is engineering-oriented; the starter's EXPERIMENTS.md is **evaluation-protocol-ready**.

4. **Research map** (`docs/RESEARCH_MAP_2026-08-17.md`) — literature positioning for gap analysis in EIA papers.

5. **CURSOR_ROADMAP milestones** — Milestone 2 self-trigger scheduler and semantic EOI roadmap items not yet implemented on either branch; this branch holds the specification.

**Verdict:** merge would either dilute `main`'s pipeline invariants or discard testable alternatives. A dedicated research branch preserves optionality and comparative power.

---

## Future Research Using This Package

Concrete investigations, ordered by near-term feasibility:

### RQ comparisons on shared Twin World scenarios

- Port or symlink `examples/autonomous_question.json` and main's Twin World fixtures so **both branches** run identical scenario IDs.
- For each RQ in EXPERIMENTS.md, record branch-specific outcomes:
  - **RQ1:** endogenous vs ambient vs delayed-user-trigger — does topology SourceMass agree with main's `AuthenticReasonVerdict`?
  - **RQ2:** drive dynamics vs threshold rules — compare starter `drives.py` against main `DriveEngine`.
  - **RQ3:** self-trigger scheduling (starter Milestone 2) vs main `LoopScheduler` Hz model.
  - **RQ4:** proactive memory policy — starter memory nodes vs main belief field persistence.
  - **RQ5:** topology metrics as predictors of counterfactual replay outcome.
  - **RQ6:** prefix-risk model vs governor-only rejection rates.

### SourceMass vs AuthenticReasonDiscriminator

- Build a paired evaluation set where initiatives are labeled `{endogenous, exogenous, ambiguous}`.
- Metrics: Cohen's κ between SourceMass `request_independence` bins and discriminator `ENDOGENOUS`/`EXOGENOUS`; ROC for EOI threshold (starter causal replay vs main `EOI_AUTHENTIC_THRESHOLD = 0.50`).
- **Hypothesis:** SourceMass catches ambient-grounded initiatives that structural discriminator misses; discriminator catches narrative-drive artifacts topology underweights.

### Threat model → adversarial harness for ContactGovernor

- Instantiate each row in THREAT_MODEL.md as a synthetic scenario (prompt injection in observation text, poisoned memory belief, engagement-maximizing drive spike, consent revocation mid-window).
- Run on **both** branches; measure bypass rate, false contact rate, and audit trail completeness.
- Deliverable: `harnesses/adversarial/` spec shared conceptually across branches.

### EXPERIMENTS.md baselines (6+ conditions) on both branches

Implement and compare:

1. Reactive  
2. Scheduled  
3. Event rule  
4. Prompt-only proactive  
5. EIA-no-drives  
6. EIA-no-memory-policy  
7. Full EIA  

Measure **EOI**, EUIR, contact burden under each condition on both implementations. Primary question: does architectural decomposition (main) change baseline ranking vs monolith (starter)?

### Milestone 2 self-trigger scheduler vs LoopScheduler Hz model

- Implement starter CURSOR_ROADMAP Milestone 2 on this branch.
- Compare contact timing efficiency (useful contacts per wall-clock hour, interruption cost integral) against main's fixed-Hz `LoopScheduler`.
- **Hypothesis:** event-driven self-trigger reduces spurious polls without missing deadline-bound initiatives.

### Semantic EOI (starter roadmap) vs structural EOI (main)

- Starter roadmap proposes semantic similarity of initiative under `do(remove user events)`; main implements structural causal replay via `TwinRunner`.
- Run divergence analysis: cases where structural EOI = 1.0 but semantic paraphrase fails (or vice versa).
- Informs whether EOI should be a multi-metric bundle in the benchmark.

### Literature from RESEARCH_MAP → gap analysis for EIA papers

- Use `docs/RESEARCH_MAP_2026-08-17.md` to draft a related-work section mapping:
  - proactive assistants / notification agents  
  - intrinsic motivation / curiosity in RL  
  - causal inference for agent behavior  
  - alignment / interruptibility  
- Identify **claim gaps** EIA can own: counterfactual endogeneity measurement, contact governor as safety boundary, Twin World falsification protocol.

---

## Branch policy

- **Do not merge** starter `src/eia/` into `main` without explicit experiment conclusion.
- Port **individual modules** (e.g., topology metrics, threat scenarios) only via small, tested PRs with comparative numbers attached.
- Keep `*.zip` and `_extracted/` gitignored on `main`; this branch holds the canonical copy of the extracted starter.

---

## Next immediate steps

1. Run `make test` on this branch; confirm 15 tests green in CI (if added).  
2. Register branch in [docs/RESEARCH_BRANCHES.md](../../docs/RESEARCH_BRANCHES.md) (done on `main`).  
3. Select one Twin World scenario ID shared with `main` and produce first paired EOI report.  
4. Open tracking issue for RQ1 SourceMass vs AuthenticReasonDiscriminator κ study.
