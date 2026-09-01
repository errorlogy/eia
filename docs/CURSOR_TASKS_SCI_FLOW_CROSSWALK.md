# Hermes CURSOR_TASKS ↔ Sci-Flow Crosswalk

**Status:** `OPERATIONAL` registry (2026-09-01)  
**Hermes backlog:** [`CURSOR_TASKS.md`](CURSOR_TASKS.md) · [`cursor_tasks.json`](cursor_tasks.json) (75 tasks, 16 P0)  
**Sci-flow branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** C2 scoped (\(E_{\mathrm{endo}}\) / ATT-E partial). **No AGI\* claim.**

---

## Purpose

Map the Hermes **75 open problems** (EIA v0.1 problematization) onto the existing **sci-flow** research program so agents pick tasks that align with M-CLI, ATT suites, metrics pool, and branch policy — without duplicating or conflicting with in-flight work.

| Frame | Canonical docs |
|-------|----------------|
| Metrics pool (M-EMP) | [`research/sci_flow/ENDOGENEITY_METRICS_POOL.md`](../research/sci_flow/ENDOGENEITY_METRICS_POOL.md) · [`endogeneity_metrics.yaml`](../research/sci_flow/endogeneity_metrics.yaml) |
| M-CLI roadmap | [`ENDOGENEITY_IMPLEMENTATION_PLAN.md`](ENDOGENEITY_IMPLEMENTATION_PLAN.md) |
| Phase 2 carryover | Implementation plan §5 Phase 2; SCI_FLOW_LOG Entry 016–017, 023 |
| M-O / OMEGA | [`OMEGA_WAVE_METRIC.md`](../research/sci_flow/OMEGA_WAVE_METRIC.md) · [`OSCILLATORY_ENDOGENEITY.md`](../research/sci_flow/OSCILLATORY_ENDOGENEITY.md) |
| ATT suites | [`AGI_TRANSITION_TEST.md`](../research/sci_flow/AGI_TRANSITION_TEST.md) · [`CAUSAL_ENDOGENEITY.md`](../research/sci_flow/CAUSAL_ENDOGENEITY.md) |
| Stable endogeneity (M-SE) | [`STABLE_ENDOGENEITY.md`](../research/sci_flow/STABLE_ENDOGENEITY.md) |

---

## Branch policy

| Branch | Scope | Hermes tasks |
|--------|-------|--------------|
| **`main`** | Production `src/eia/` — Governor, DriveEngine, audit/EOI, eval harnesses, CI, arXiv, constitution | **A–F, H, I** (theory, drives, governor, metrics instrumentation, eval worlds, NAMM, infra, paper) |
| **`research/cursor-starter-v0.2-woe-eis`** | WoE sandbox, ATT runners, M-CLI, endogeneity stack sim, daemon carryover research | **Overlaps with D/E** where twin/ATT/DSR; **G** bridge docs; **sci-flow-only** work (Phase 2, M-O, pool ticks) |
| **Hermes runtime** (external) | `~/.hermes/`, `hermes-agent` | **G01–G04** only — not merged into `main/src/eia/` |

**Hard stop:** Do not merge WoE research runtime into `main/src/eia/` (same rule as sci-flow skill).

---

## Highlighted overlaps (priority bridges)

| Hermes ID | Hermes task | Sci-flow / M-CLI anchor | Notes |
|-----------|-------------|-------------------------|-------|
| **B05** | No-LLM-mood test (`DriveEngine` ≠ embedding/LLM) | **M-CLI Phase 0–1** · `model_roles.att_evidence.llm_allowed: false` · constitution `no_llm_mood: true` | **Main** — add `tests/test_no_llm_mood.py`. Enforces Tier 0: drives are not LLM mood proxies. |
| **D01** | EOI-k (k=1,5,20) twin sweep | **ATT-E** · Tier A `E_ENDO` / `CF4_E_PARTIAL` · main `TwinRunner` + research CF-4 | **Main** instrumentation; **research** interprets under causal bar (`do(o=∅)`). Not a C2 raise alone. |
| **D05** | DSR — 50 ticks, `d>0.3` persistence | **M-SE** · Tier B `B_D` · [`STABLE_ENDOGENEITY.md`](../research/sci_flow/STABLE_ENDOGENEITY.md) · `endogeneity_stack_sim.py` | **Research** — longitudinal drive sustainability; pairs with **E04**. Phase 2 carryover strengthens DSR evidence. |
| **G05** | P4→P5 bridge doc | **Partial** — `docs/HERMES_EIA_BRIDGE.md` **not yet written**; sci-flow has [`MIOC_EIA_BRIDGE.md`](../research/sci_flow/MIOC_EIA_BRIDGE.md) (MIOC Ω, not Hermes) | **Docs** on either branch; G05 is Hermes-specific star→ring topology. |
| **A04** | Pearl DAG for EOI | **CAUSAL_ENDOGENEITY** · ATT-E falsifiers F-EXT, F-NODO | **Main/docs** — figure for arXiv; aligns with `do(o=∅)` intervention narrative. |
| **B01** | Drive ablation 3×2 | **M-SE ablation** · stack sim drive-field toggles | **Research** — similar matrix in `endogeneity_stack_sim.py`; Hermes harness uses `loop_max_123.py` on main. |
| **C02** | V2 soft-defer freeze | **Main governor** — AuthenticReason production gate | **Main** only; sci-flow must not lower thresholds for science. |
| **E04** | Longitudinal 50 ticks | **D05 DSR** · M-R-LIVE gap · **Phase 2 carryover** | **Research** — same experiment family as DSR; daemon carryover closes ATT-R live gap. |
| **D08** | Kappa study | **M-B finding** (SourceMass vs AuthenticReason) · SCI_FLOW_LOG Entry 003 | **Main/research** — already documented κ asymmetry; Hermes formalizes. |
| **F01** | NAMM hermetic harness | **T_NAMM_cert** optional soft ATT-N witness | **Main** CI; sci-flow treats as soft structural witness only. |

### M-O / OMEGA (no direct Hermes task)

Sci-flow **M-O** (oscillatory substrate, `OMEGA_t`) has **no 1:1 Hermes task**. Closest Hermes neighbors:

| Hermes | Relation to M-O |
|--------|-----------------|
| B03/B04 decay/saturation | Drive dynamics parameters; M-O feeds \(\Phi_t\) not substitute for decay tables |
| B06 novelty `n_{k,t}` | Could wire from `M_t` / oscillatory novelty — explore adjunct |
| A03 autopoiesis | Theoretical framing for endogenous loops; not oscillation proof |

**Rule:** High OMEGA_t without ATT-E / genesis linkage = Tier C decorative ([`ENDOGENEITY_METRICS_POOL.md`](../research/sci_flow/ENDOGENEITY_METRICS_POOL.md) §Tier C).

---

## Category → sci-flow mapping

### A. Theory & Formalism → docs + main schemas

| IDs | Branch | Sci-flow link |
|-----|--------|---------------|
| A01, A05, A08 | main | Constitution / schemas; no ATT claim |
| A02, A03, A06, A07, A09, A10 | main + arxiv | Paper problematization; A03 cites **B05 no_llm_mood** |
| **A04** [P0] | main | **CAUSAL_ENDOGENEITY** DAG figure |

### B. Drive & BeliefField → main `src/eia/drives/` + M-SE

| IDs | Branch | Sci-flow link |
|-----|--------|---------------|
| **B01** [P0], B02, B08 | main + research | M-SE drive field; ablation in stack sim |
| **B05** [P0] | main | **M-CLI Tier 0** LLM ban on drives |
| B03, B04, B10 | main/docs | MATHEMATICS.md; stack sim hyperparams |
| B06–B07, B09 | main | Engineering; B07 couples Governor ↔ drives |

### C. Governor & Safety → main only

All **C** tasks are **main** production path. Sci-flow **must not** lower `min_contact_score` for evidence (NEXT_SCI_AGENT_PROMPT stop rule). C01 ROC calibration feeds main EOI gate, not ATT C-ladder.

### D. Metrics & EOI → main audit + research ATT

| IDs | Branch | Pool tier / ATT |
|-----|--------|-----------------|
| **D01** [P0] | main + research | Tier A **ATT-E** (EOI-k windows) |
| **D02** [P0] | main | Source Autonomy; EIS audit (M-B) |
| D03, D06, D07, D10 | main | Explore metrics; not pool Tier A |
| **D04**, **D05**, **D09** [P0] | main + research | D05 → **M-SE B_D**; D09 harmonization with twin policies |
| D08 | main/research | κ study (M-B legacy) |

### E. Evaluation & Datasets → main evals + research experiments

| IDs | Branch | Sci-flow link |
|-----|--------|---------------|
| **E01**, **E02**, **E10** [P0] | main | G2 gate; held-out ADV aligns with ATT falsifiers |
| E03–E09 | main/research | Baselines and protocols |
| **E04** [P1] | research | **Phase 2 carryover** + DSR |

### F. NAMM & Compression → main harnesses

F01 → T_NAMM_cert (optional). F03/F04 trace manifold — paper explore, no sci-flow C claim.

### G. Hermes × EIA Bridge → docs + external Hermes

| IDs | Branch | Status |
|-----|--------|--------|
| G01–G04 | Hermes external | Runtime integration; not sci-flow merge |
| **G05** [P1] | docs | **Open** — complements MIOC bridge, not duplicate |

### H. Infra & Repro → main

H01 CI gates align with `make check-sci-tier0` on research branch; main pytest gates separate.

### I. Paper & Docs → main

I01 arXiv problematization can cite this crosswalk + CURSOR_TASKS as roadmap (I06 banner).

---

## P0 tasks aligned with current next steps

Sci-flow **current priority** (NEXT_SCI_AGENT_PROMPT): metrics pool Tier A/B ticks · optional **Phase 2 daemon carryover** · M-O do(Omega) shadow · no new C-level without pre-registration.

| P0 ID | Title | Aligns now? | Recommended branch | Action |
|-------|-------|-------------|-------------------|--------|
| **B05** | No-LLM-mood test | **Yes** — M-CLI Tier 0 lock | main | Implement test; unblocks drive/governor trust |
| **D01** | EOI-k sweep | **Yes** — ATT-E / pool `E_ENDO` | main + research | Extend TwinRunner; report in metrics pool |
| **D05** | DSR 50 ticks | **Yes** — M-SE stable endogeneity | research | Run with stack sim / E04; Phase 2 strengthens |
| **B01** | Drive ablation | **Partial** — M-SE ablation exists | main + research | Cross-check loop_max vs stack sim matrix |
| **A04** | Pearl DAG | **Partial** — causal docs | main | arXiv figure; supports ATT-E narrative |
| **C02** | V2 soft-defer freeze | main production | main | Independent of sci-flow loop |
| **C01**, **D04**, **E01**, **E02**, **E10** | Eval / G2 / ROC | main meta-loop | main | Parallel track to sci-flow |
| **H01** | CI gates | Both | main + research | research has `eia-sci-tier0.yml` |
| **I01** | arXiv v0.1 | docs | main | Roadmap points to CURSOR_TASKS |

**Not current sci-flow priority (still P0 for product):** C01, C03, D02, D04, D09, E01, E02, E10, H01, I01 — main-stack / G2 / arXiv path.

---

## Agent routing

| If you are… | Pick tasks from… | Read first |
|-------------|------------------|------------|
| Sci-flow `/loop` on research branch | D01, D05, E04, B01 (research interpretation); Phase 2 carryover | `NEXT_SCI_AGENT_PROMPT.md`, metrics pool |
| Main-stack Cursor agent | B05, C*, D02, D09, H01, I* | `docs/CURSOR_TASKS.md`, `src/eia/` tests |
| Hermes integration | G01–G05 | G05 doc draft; do not merge WoE into main |
| Paper / arXiv | A*, I* | `arxiv/main.tex`, this crosswalk |

---

## Machine-readable index

JSON task IDs match [`cursor_tasks.json`](cursor_tasks.json). For automation, filter by:

```json
{"pri": "P0"}
```

Crosswalk fields (future): add `sci_flow_ref`, `branch`, `pool_tier` to JSON in a later tick — not required for v0.1 integration.

---

## Related documents

| Doc | Role |
|-----|------|
| [`NEXT_SCI_AGENT_PROMPT.md`](NEXT_SCI_AGENT_PROMPT.md) | Sci agent handoff + Hermes backlog link |
| [`ENDOGENEITY_IMPLEMENTATION_PLAN.md`](ENDOGENEITY_IMPLEMENTATION_PLAN.md) | M-CLI Phases 0–6 |
| [`SCI_FLOW_LOG.md`](SCI_FLOW_LOG.md) | Entry 026 — integration log |
| [`.cursor/skills/eia-sci-flow/SKILL.md`](../.cursor/skills/eia-sci-flow/SKILL.md) | Branch scope + CURSOR_TASKS pointer |
