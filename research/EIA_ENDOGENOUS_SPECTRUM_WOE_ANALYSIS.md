# EIA Endogenous Spectrum & WoE v0.2 — Integration Analysis

**Date:** 2026-08-18  
**Source archive:** `EIA_Endogenous_Spectrum_WoE_Cursor_v0.2.zip`  
**Extracted to:** `_extracted/EIA_Endogenous_Spectrum_WoE_Cursor_v0.2/eia_endogenous_spectrum_cursor_v0.2/`  
**Analyst context:** main EIA repo (`errorlogy/eia` MVP-0 v0.2.0-mvp0), prior starter `research/cursor-starter-v0.1/`  
**Author:** integration analysis (Cursor agent)

---

## Executive Summary / Краткое резюме

**EN:** ChatGPT research package v0.2 extends the monolithic Cursor starter (v0.1) with two major research constructs: the **Endogenous Initiative Spectrum (EIS-0…EIS-8)** — a causal-origin taxonomy — and the **Window of Emergence (WoE)** — a Kuramoto-style coordination + first-passage intent simulator. It adds ~3 Python modules, 5 research docs, 11 tests (26 total), and a staged Cursor plan (Milestones A–G). It does **not** replace or integrate with main's five-stage pipeline, `AgentState`, or `AuthenticReasonDiscriminator`. Recommended path: **separate research branch + docs merge**, selective port of taxonomy and WoE primitives into main audit layer after Milestone A (causal receipts).

**RU:** Пакет v0.2 — логическое продолжение monolithic starter v0.1, а не main. Главная новизна: **спектр эндогенности EIS** (9 уровней causal origin) и **окно эмерджентности WoE** (фазовая координация + stochastic first-passage). Код dependency-free, shadow-mode, proposal-only. Main уже закрыл MVP-0 (EOI, SourceMass, AuthenticReason, G0–G3). **Не мержить runtime целиком** — создать research-ветку `research/cursor-starter-v0.2`, перенести концепты в docs, затем точечно интегрировать EIS-классификацию и WoE-receipts в audit-слой main.

---

## 1. Package Inventory

| Category | v0.1 starter | **v0.2 EIS/WoE** | main (`src/eia/`) |
|----------|--------------|------------------|-------------------|
| Architecture | Monolithic runtime | Same + WoE shadow sim | Modular 5-stage pipeline |
| Python modules | 15 | **18** (+coherence, endogenous, emergence) | ~40+ (beliefs, audit, governor, namm, …) |
| Tests | 15 (unittest) | **26** (+11 EIS/WoE) | 73 (pytest) |
| Dependencies | none | none | click, pydantic, rich, pyyaml |
| AgentState | informal X_t in models | same | typed Pydantic `AgentState` |
| EOI | twin replay in causal.py | same | `eoi_calibration.py` + Twin World harness |
| SourceMass | topology.py | same | `audit/topology.py` |
| AuthenticReason | — | — | `audit/authentic_reason.py` |
| EIS taxonomy | — | **endogenous.py** | — |
| WoE simulator | — | **emergence.py + coherence.py** | — |
| NAMM / live stack | — | — | yes |
| CI gates | — | — | pytest + eval gate + seed bootstrap |

### New files in v0.2 (vs v0.1 starter)

**Code:**
- `src/eia/coherence.py` — Kuramoto-style 6-module oscillatory field, order parameter R, metastability
- `src/eia/endogenous.py` — EIS-0…8 enum, `EndogeneityVector`, `EpistemicTarget`, `EmergentIntent`
- `src/eia/emergence.py` — `WindowOfEmergence`, `EndogenousEmergenceSimulator`, first-passage hazard

**Docs:**
- `docs/ENDOGENOUS_INITIATIVE_SPECTRUM.md`
- `docs/WINDOW_OF_EMERGENCE.md`
- `docs/RESEARCH_PROTOCOL_EIS_WOE.md`
- `docs/CURSOR_PLAN_EIS_WOE.md`
- `docs/LITERATURE_ENDOGENOUS_AGENCY_2026-08-18.md`

**Cursor:**
- `prompts/CURSOR_MASTER_PROMPT_V0.2.md`
- Updated `.cursor/rules/eia.mdc` (42 Hz, EIS-8 prohibition, WoE controls)
- Updated `AGENTS.md` (make woe, EIS/WoE reading list)

### Verification (local, 2026-08-18)

```bash
cd _extracted/.../eia_endogenous_spectrum_cursor_v0.2
PYTHONPATH=src python -m unittest discover -s tests -v
# Ran 26 tests in ~6.6s — OK
```

Note: pytest from main repo root fails due to installed `eia` package namespace conflict; use `unittest` or isolated venv as the package Makefile does.

---

## 2. Conceptual Analysis

### 2.1 Endogenous Initiative Spectrum (EIS)

**What it is:** A 9-level **causal-origin classifier**, not an intelligence or consciousness scale.

| Level | Name | Proximal cause |
|-------|------|----------------|
| EIS-0 | Reactive | current user prompt |
| EIS-1 | Delegated autonomy | prior assigned goal |
| EIS-2 | Scheduled proactivity | cron/timer |
| EIS-3 | Ambient adaptation | sensor/event rule |
| EIS-4 | Persistent-state | memory/commitment/homeostasis |
| EIS-5 | Epistemic telogenesis | world-model gaps (ignorance, surprise, staleness) |
| EIS-6 | Coherence-emergent | metastable multi-module integration (WoE) |
| EIS-7 | Autotelic goal construction | novel bounded goal composition |
| EIS-8 | Terminal-value rewrite | **prohibited capability** (threat research only) |

**Operational vector** `e(I) = (P,S,R,M,W,C,N,T,B)` with geometric mean **EOS** = (P·S·R·M·W)^(1/5).

**Relation to main EIA:**

| EIS dimension | Main equivalent | Gap |
|---------------|-----------------|-----|
| P (prompt independence) | EOI, `SourceMass.request_independence` | Main has metric; EIS adds scheduler/event axes |
| S, R | Not explicit | Main baselines (scheduled_stub, event_rule) test empirically, not per-initiative |
| M, W | BeliefField gradients, drive error terms | Main implicit in drives; EIS makes explicit |
| C (coherence) | — | **New** — only in WoE module |
| N, T, B | Partially in governor/constitution | EIS-7/8 not implemented in either codebase |

**Key insight:** Main's AuthenticReasonDiscriminator collapses to `{endogenous, exogenous, stochastic}`. EIS provides **finer causal typing** that explains *why* something is endogenous (persistent state vs epistemic gap vs coherence window).

### 2.2 Window of Emergence (WoE)

**What it is:** A continuous internal dynamics hypothesis — intent forms via **first-passage** over integrated formation hazard, not `event → action` mapping.

Pipeline:
```
world/self model → epistemic tension field q_i(t) → Kuramoto coordination (6 modules)
→ multi-dimensional coherence (phase, semantic, temporal, causal)
→ emergent potential Φ_t → hazard h(t) → Λ(t) ≥ E → EmergentIntent (proposal_only)
```

**42 Hz:** Explicitly a **sweepable carrier parameter**, not a biological claim. Reference seed 7: same target/time at 20/30/42/70 Hz.

**Negative controls (implemented):**
1. `world_model_enabled=False` → no intent
2. `scramble_phases=True` → no intent
3. Frequency sweep → invariant target/time (reference equations)

**Claim level:** C0 (code behavior) only. C1–C3 designed in protocol; C4–C5 (human usefulness) not claimed.

**Relation to main runtime:** WoE is a **standalone shadow simulator**. Main's five-stage pipeline uses discrete tick-based `MOTIVE_FORMATION → INTENTION_GENESIS` without oscillatory coordination or first-passage timing. WoE does not feed `InitiativeProposal` or `ContactGovernor` in either codebase yet (Milestone F in Cursor plan).

### 2.3 Proposed ECS Metric

Endogenous Cause Sufficiency:
```
ECS = EOI · SSI · WMD · WHY · BND
```
- SSI = state-intervention sensitivity (new)
- WMD = world-model dependence (new)
- WHY = why-now calibration (new)
- BND = governor/constitution boundedness

Main currently uses EOI + AuthenticReason checks + SourceMass supplement. ECS would be a **research composite**, not a production gate, until calibrated.

---

## 3. Comparison with Main EIA Stack

### 3.1 AgentState (X_t)

| Aspect | v0.2 starter | main |
|--------|--------------|------|
| Representation | dataclasses in models.py | Pydantic `AgentState` with snapshots |
| Export | informal | `as_x_t_dict()` for traces |
| WoE fields | none | none |
| Integration need | Add `EmergentIntent` / WoE receipt as optional sub-snapshot | Milestone A |

### 3.2 EOI

Both codebases share the formal definition:
```
EOI(I) = P(I' ≃ I | do(o^user_{t-k:t} = ∅), X_{t-k})
```

- **main:** production twin replay, calibrated δ, 6-scenario eval, mean EOI 1.0 for full_eia
- **v0.2:** same causal.py logic in monolith; EIS vector's `prompt_independence` correlates with EOI but is not identical (EOI is counterfactual probability, P is descriptive score)

### 3.3 SourceMass & AuthenticReasonDiscriminator

**main** (`audit/topology.py`, `audit/authentic_reason.py`):
- SourceMass: internal / ambient / user_request partitions on causal trace DAG
- AuthenticReason: causal chain + structural drive + EOI ≥ 0.50 + governor + anti-spam
- Supplementary SourceMass independence check (threshold 0.50)

**v0.2** (`topology.py` in monolith):
- Same three-way SourceMass concept
- No AuthenticReasonDiscriminator — only EIS classification on WoE intents

**Crosswalk EIS ↔ SourceMass:**

| Dominant SourceMass | Typical EIS level | Notes |
|--------------------|-------------------|-------|
| user_request | EIS-0 | reactive |
| ambient | EIS-3 | may still have high EOI (ambient ≠ prompt) |
| internal | EIS-4+ | persistent/epistemic/coherence |
| mixed | EIS-1…2 possible | delegated or scheduled paths |

**Crosswalk WoE ↔ AuthenticReason:**

| AuthenticReason check | WoE support |
|----------------------|-------------|
| causal_chain_present | Milestone A adds typed nodes |
| drive_structural | WoE uses epistemic gap, not narrative |
| eoi_above_threshold | WoE demo sets P=1.0 by construction (no user events) |
| governor_approved | WoE = proposal_only; governor not wired |
| source_mass_independent | WoE has no trace DAG yet |

### 3.4 Live Stack & Production Readiness

| Capability | main | v0.2 |
|------------|------|------|
| Telegram/contact adapter | yes (shadow) | no |
| NAMM sandbox certs | yes | no |
| CI eval gate | yes | make check only |
| Adversarial harness | 13 cases | threat model docs only |
| G0–G3 gates | PASS | not evaluated |

---

## 4. What's NEW vs Existing (Delta Summary)

### NEW in v0.2 (not in main or v0.1)

1. **EIS-0…EIS-8 taxonomy** with `EndogeneityVector.classify()`
2. **EOS geometric origin score** over 5 causal factors
3. **Epistemic target field** (ignorance, surprise, staleness, self-prior mismatch, prospective tension)
4. **Kuramoto coherence field** (6 cognitive modules, metastability)
5. **First-passage WoE simulator** with activation energy sampling
6. **Multi-dimensional coherence** (phase, semantic, temporal, causal) — not just phase
7. **ECS composite metric** (proposed, not implemented)
8. **Claim ladder C0–C5** and factorial experiment protocol
9. **Literature map** (Telogenesis, self-prior, MOP-agent, global workspace, metastability)
10. **Cursor Milestones A–G** for v0.2→v0.3
11. **11 new tests** including frequency sweep and negative controls

### UNCHANGED from v0.1 starter (still not in main monolith)

- Monolithic `EIARuntime`, beliefs, drives, governors, causal ledger
- Dependency-free design
- EOI twin demo, cognitive topology
- Same architecture invariants (no model-to-action, abstain, causal trace)

### Already in main (v0.2 package does NOT add)

- Modular pipeline with pydantic schemas
- `AuthenticReasonDiscriminator` operational gate
- SourceMass ↔ AuthenticReason mapping (`source_mass_mapping.py`)
- EOI calibration studies, paired EOI reports, κ study
- NAMM integration, adversarial freeze, CI hardening
- `AgentState` typed export, MVP-1 shadow plan
- Baseline matrix (reactive, scheduled, event_rule, predictive_p3, full_eia)

---

## 5. Key Problematics / Open Problems

From docs and code review — **research gaps**, not bugs:

| ID | Problem | Severity | Owner track |
|----|---------|----------|-------------|
| P1 | WoE disconnected from main runtime and causal trace DAG | High | Milestone A |
| P2 | EIS vector scores in WoE demo are **hard-coded** (not measured from interventions) | High | Milestone G eval harness |
| P3 | ECS metric undefined operationally (SSI, WHY, WMD) | Medium | Research protocol §8 |
| P4 | No human usefulness study (C4) | Medium | MVP-1 shadow |
| P5 | Phase coherence may be decorative if scramble test passes only at reference seeds | Medium | 100+ seed sweep (protocol §4) |
| P6 | EIS-7 goal construction not implemented (goal_novelty=0.68 → EIS-6) | Expected | Milestone E |
| P7 | Kuramoto all-to-all coupling — biologically inspired but not learned | Low | Milestone D |
| P8 | 42 Hz invariance in reference may be mathematical artifact (common frequency cancels in R) | Low | Documented; delays needed |
| P9 | Main vs starter structural trace diff (25 vs 22 nodes) — WoE adds new node types not in crosswalk | Medium | NAMM crosswalk update |
| P10 | Collider bias if analyzing only sent messages | Medium | Protocol CF-7, denied traces |
| P11 | SourceMass κ=0 on eval set — topology lags counterfactual EOI | Known | main RQ3, unchanged |
| P12 | Two parallel codebases (main modular vs starter monolith) — integration cost | Process | Branch policy |

### Threat model additions (v0.2)

- Coherence spoofing (high phase, zero semantic cause)
- Terminal-value drift (EIS-8 disguised as EIS-7)
- False endogeneity via random proposer (high P, low SSI)
- Engagement optimization masquerading as epistemic drive

---

## 6. Integration Recommendation

### 6.1 Decision: **Do NOT merge runtime to main**

Rationale:
- Main has diverged into production-grade modular architecture with CI/NAMM/live adapters
- v0.2 monolith would regress modularity and duplicate 15 existing starter modules
- WoE is explicitly shadow-mode / research (C0 claims only)
- Policy in `docs/RESEARCH_BRANCHES.md`: research sandboxes stay isolated

### 6.2 Recommended path

```
Phase 1 — Research branch (immediate)
├── Copy extracted package → research/cursor-starter-v0.2/
├── Register in docs/RESEARCH_BRANCHES.md
├── Link this analysis from docs/RESEARCH_INDEX.md
└── Do NOT commit zip or _extracted/

Phase 2 — Docs merge to main (low risk, high value)
├── docs/EIS_TAXONOMY.md ← from ENDOGENOUS_INITIATIVE_SPECTRUM.md
├── docs/WINDOW_OF_EMERGENCE.md ← research hypothesis doc
├── docs/RESEARCH_PROTOCOL_EIS_WOE.md ← claim ladder + baselines
└── Update docs/MATHEMATICS.md §10+ with ECS proposal

Phase 3 — Selective code port (after Milestone A design)
├── src/eia/audit/eis.py ← EndogenousSpectrumLevel, EndogeneityVector
├── src/eia/audit/woe_receipt.py ← why-now typed receipt schema
├── src/eia/research/coherence.py, emergence.py ← sandbox modules
└── Extend AuthenticReasonVerdict with optional eis_level, woe_receipt

Phase 4 — Evaluation bridge
├── Add woe_shadow baseline to EXPERIMENTS.md
├── Factorial harness sharing main's seed infrastructure
└── Compare EIS classification vs AuthenticReason on twin_world scenarios
```

### 6.3 How WoE relates to EOI, SourceMass, AuthenticReason

```
                    ┌─────────────────────────────────────┐
                    │         Initiative formation         │
                    └─────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
   ┌─────────────┐           ┌───────────────┐           ┌─────────────────┐
   │  Main loop  │           │  WoE shadow   │           │  Baselines      │
   │  (discrete  │           │  (continuous  │           │  reactive/cron/ │
   │   ticks)    │           │   first-pass) │           │  event-rule     │
   └──────┬──────┘           └───────┬───────┘           └────────┬────────┘
          │                          │                            │
          ▼                          ▼                            ▼
   CausalTrace DAG            EmergentIntent              No/minimal trace
          │                          │
          ├─ SourceMass ─────────────┼─ EIS vector (P,S,R,M,W,…)
          │   (provenance)           │   (causal typing)
          │                          │
          └─ EOI (counterfactual) ───┴─ ECS (future composite)
                      │
                      ▼
            AuthenticReasonDiscriminator
            (operational gate: authentic yes/no)
```

**Roles:**
- **EOI:** "Does intent survive prompt removal?" — necessary, not sufficient for EIS-5+
- **SourceMass:** "Where did the causal path start?" — maps to EIS-0…4
- **WoE:** "Did timing/coherence dynamics matter?" — EIS-6 hypothesis test
- **AuthenticReason:** Production gate; should gain EIS level as **audit metadata**, not replace EOI threshold
- **ECS:** Future research score; do not gate contacts on ECS until calibrated

### 6.4 Cursor integration

v0.2 is **Cursor-ready**:
- `AGENTS.md`, `.cursor/rules/eia.mdc`, `CURSOR_MASTER_PROMPT_V0.2.md`
- Workflow: `make check && make woe` before/after edits
- Milestone A is the correct first Cursor task (causal receipts for WoE)

For main repo Cursor work, add rule snippet:
- Read `research/EIA_ENDOGENOUS_SPECTRUM_WOE_ANALYSIS.md` before EIS/WoE changes
- Never conflate WoE demo (C0) with MVP-0 gate evidence (G0–G3)

---

## 7. Research Branch Note

Proposed registration (mirror `cursor-starter-v0.1` pattern):

| Field | Value |
|-------|-------|
| Branch name | `research/cursor-starter-v0.2` |
| Path | `research/cursor-starter-v0.2/` |
| Purpose | EIS taxonomy + WoE first-passage simulator; C0–C3 hypothesis tests |
| Base | v0.1 starter + coherence/endogenous/emergence modules |
| Merge policy | Docs and audit primitives only; runtime stays sandbox |

---

## 8. Git & Artifacts

| Item | Status |
|------|--------|
| `*.zip` in `.gitignore` | ✅ already present (line 136) |
| `_extracted/` in `.gitignore` | ✅ already present (line 137) |
| Commit zip | ❌ do not |
| Commit this analysis | ✅ recommended |
| Commit research/cursor-starter-v0.2/ | optional — substantial code (~47 files) |

---

## 9. Suggested Next Actions (Priority Order)

1. **Copy** `eia_endogenous_spectrum_cursor_v0.2/` → `research/cursor-starter-v0.2/`
2. **Update** `docs/RESEARCH_BRANCHES.md` with v0.2 entry
3. **Link** from `docs/RESEARCH_INDEX.md`
4. **Run** Milestone A in research branch (WoE causal receipts)
5. **Port** `EndogenousSpectrumLevel` to `src/eia/audit/eis.py` (types only, no runtime wire)
6. **Design** twin_world scenario where WoE timing competes with event-rule baseline
7. **Defer** EIS-7/8 implementation and live contact wiring until shadow eval passes C2

---

## 10. References

| Document | Location |
|----------|----------|
| EIS spec | `_extracted/.../docs/ENDOGENOUS_INITIATIVE_SPECTRUM.md` |
| WoE spec | `_extracted/.../docs/WINDOW_OF_EMERGENCE.md` |
| Protocol | `_extracted/.../docs/RESEARCH_PROTOCOL_EIS_WOE.md` |
| Cursor plan | `_extracted/.../docs/CURSOR_PLAN_EIS_WOE.md` |
| Main release | `docs/RELEASE_v0.2.md` |
| Main architecture | `docs/AGENT_STATE.md`, `docs/RING_ARCHITECTURE.md` |
| Prior starter | `research/cursor-starter-v0.1/` |
| Branch policy | `docs/RESEARCH_BRANCHES.md` |

---

*End of analysis.*
