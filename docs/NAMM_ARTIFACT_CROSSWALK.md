# NAMM ↔ EIA Pipeline Artifact Crosswalk

**Status:** v0.1 research mapping  
**Author:** Roman Kuznetsov — [anthemium.tech](https://anthemium.tech)  
**Date:** August 17, 2026

Maps the EIA cognitive pipeline (`observation → comprehension → motive → intention → initiative`) to NAMM verification artifacts, experiments, and Hz-band analogies from the `hypothesis/cognitive-antigravity` branch.

**Related:** [`NAMM_INTEGRATION.md`](./NAMM_INTEGRATION.md) · [`NAMM_SCI_LIBRARIES.md`](./NAMM_SCI_LIBRARIES.md) · [`SCI_FLOW_PLAN.md`](./SCI_FLOW_PLAN.md) · NAMM [`docs/BRAINWAVE_OSCILLATION_HYPOTHESIS.md`](https://github.com/errorlogy/namm-experiments/blob/main/docs/BRAINWAVE_OSCILLATION_HYPOTHESIS.md) · [`docs/AI_THINKING_TOPOLOGY.md`](https://github.com/errorlogy/namm-experiments/blob/main/docs/AI_THINKING_TOPOLOGY.md) · [`docs/COGNITIVE_ANTIGRAVITY_HYPOTHESIS.md`](https://github.com/errorlogy/namm-experiments/blob/main/docs/COGNITIVE_ANTIGRAVITY_HYPOTHESIS.md) · NAMM [`docs/SCI_FLOW.md`](https://github.com/errorlogy/namm-experiments/blob/main/docs/SCI_FLOW.md)

---

## 1. Five-stage pipeline crosswalk

| EIA Stage | Scientific term (EIA spec) | NAMM artifact / experiment | How it helps |
|-----------|---------------------------|----------------------------|--------------|
| **ObservationIngest** | `ObservationEvent`, sensor fabric (L2–L4) | *(none at ingest)* — event backbone only | Raw events enter with provenance; NAMM gates apply only after structural comprehension, not at sensor boundary |
| **SenseMaking** | Belief update, world model (L5), `BeliefState` | **NAMM-2026-006** (TDA frame) · **NAMM-2026-004** (meta-evaluator topology) · `docs/AI_THINKING_TOPOLOGY.md` | BeliefField contradictions map to **topological tension** (β₁ holes, inconsistency energy); dual-belief conflict triggers TDA persistence scaffold; epistemic+coherence joint threshold triggers fixed-point meta-evaluator reference |
| **MotiveFormation** | `MotivationSignal[]`, DriveEngine (L7) | **NAMM-2026-013** (cognitive antigravity, H-CA-001) · **NAMM-2026-003** (program AST) · `K_A`/`K_H` asymmetry · `compute_antigravity_scores` | Drives computed from **structural gradients** (not embedding median) — operational analog of escaping \(M_0(q_H)\) homo-attractor; epistemic spike queues internal math sandbox (003); coherence+epistemic triggers antigravity protocol (013) |
| **IntentionGenesis** | `IntentionCandidate[]`, competing proposals (L9–L10) | **NAMM-2026-004** (evaluator competition) · **NAMM-2026-007** (raw tensor invariants) | Multiple candidates = meta-evaluator fixed-point arbitration; machine-native vocabulary when competence proxy high |
| **InitiativeEmission** | Endogenous act selection, `Initiative` | **NAMM-2026-001** (calibration null-result discipline) | Every emission logged against falsifiability baseline — rejections are first-class |
| **ContactGovernor** | `ContactDecision`, independent clearance (L12) | **Protocol v2 attack checklist** · `certificate.json` lineage | No external contact citing NAMM result without verified certificate; governor uses same falsifiability mindset as SNH gates |

Implementation config: [`config/namm_crosswalk.yaml`](../config/namm_crosswalk.yaml)

---

## 2. Hz bands ↔ EIA runtime loops (L-A … L-O)

EIA spec §13 defines multi-scale runtime loops. NAMM [`BRAINWAVE_OSCILLATION_HYPOTHESIS.md`](https://github.com/errorlogy/namm-experiments/blob/main/docs/BRAINWAVE_OSCILLATION_HYPOTHESIS.md) provides **research scaffolding** (not literal EEG claims) linking Hz bands to cognitive topology.

| EIA Loop | Spec frequency | Pipeline stage | NAMM Hz band analogy | NAMM experiment / doc |
|----------|---------------|----------------|---------------------|----------------------|
| **L-A** Emergency safety | 20–1000 Hz | ObservationIngest | **gamma** (30–80 Hz) — fast binding | — |
| **L-B** Sensor integrity | 1–100 Hz | ObservationIngest | **beta** (13–30 Hz) — invariant maintenance | — |
| **L-C** Perception | 1–30 Hz | ObservationIngest | **beta** | — |
| **L-D** Situation update | 0.2–10 Hz | SenseMaking | **theta** (4–8 Hz) — context integration | NAMM-2026-006 (TDA) |
| **L-E** Salience | event-driven | SenseMaking | **theta** | — |
| **L-F** Drive/homeostasis | 10 sec–30 min | MotiveFormation | **alpha** (8–12 Hz) — homo/median gating escape | NAMM-2026-013 |
| **L-G** Intention genesis | on threshold | IntentionGenesis | **high-gamma** (80–150 Hz) — insight bursts | NAMM-2026-004 |
| **L-H** Deliberation | on candidate | IntentionGenesis | **high-gamma** | NAMM-2026-004 |
| **L-I** Contact arbitration | contact proposal | ContactGovernor | **alpha** — interrupt gating | Protocol v2 |
| **L-J** Dialogue | on turn | InitiativeEmission | — | — |
| **L-K** Action execution | on ticket | InitiativeEmission | — | — |
| **L-L** Reflection | after episode | — | **theta–gamma nesting** | NAMM-2026-014 |
| **L-M** Memory consolidation | hours/days | SenseMaking | **delta** (0.5–4 Hz) | — |
| **L-N** Self-calibration | days/week | MotiveFormation | — | — |
| **L-O** Policy/audit | continuous | ContactGovernor | — | Protocol v2 |

`LoopScheduler` stub: `src/eia/scheduler/` — resolves active loops per pipeline stage from `config/namm_crosswalk.yaml`.

**Epistemic note:** Hz mappings are `CONJECTURE` / `PHILOSOPHICAL_INFERENCE` per NAMM labeling — useful for director-layer routing and covariates (014), not certificate gates.

---

## 3. NAMM experiment quick reference

| Experiment | Domain | EIA hook stage | Artifact |
|------------|--------|----------------|----------|
| NAMM-2026-001 | `finite_graphs` | InitiativeEmission | Null calibration — rejections.jsonl discipline |
| NAMM-2026-002 | `rewriting` | — (future internal sandbox) | Confluent rewrite certificates |
| NAMM-2026-003 | `program_ast` | MotiveFormation | AST synthesis when epistemic drive high |
| NAMM-2026-004 | `meta_evaluation` | SenseMaking, IntentionGenesis | Fixed points E ≈ F(E) — AI thinking topology |
| NAMM-2026-005 | `open_problem_shadow` | — (future) | Kotzig P_k counterexample shadow |
| NAMM-2026-006 | `tda_frame` | SenseMaking | Persistent homology on belief-graph metric |
| NAMM-2026-007 | `raw_tensor` | IntentionGenesis | Machine-native tensor invariants (F3g) |
| NAMM-2026-008 | `rewriting` (extended) | MotiveFormation (future) | Confluence certificates — **stub**; adapter logs intent only |
| NAMM-2026-009 | `finite_graphs` (calibration v2) | InitiativeEmission | Extended null-result discipline — **stub** |
| NAMM-2026-010 | `open_problem_shadow` | SenseMaking (future) | Counterexample shadow search — **stub** |
| NAMM-2026-013 | `meta_evaluation` | MotiveFormation | Cognitive antigravity v1 (H-CA-001) — **runnable** via `run_sandbox()` |
| NAMM-2026-014 | oscillation covariates | Reflection (L-L) | Ω_c / band-coherence vs 013 arms — **stub** |

---

## 4. Cognitive antigravity ↔ BeliefField drives

NAMM cognitive antigravity (`hypothesis/cognitive-antigravity`) targets **median embedding gravity** — LLM collapse toward corpus-typical answers (\(M_0\)).

EIA BeliefField drives are **structurally orthogonal**:

| NAMM construct | EIA construct |
|----------------|---------------|
| \(D_{\mathrm{med}}\) distance from median | BeliefField gradient (entropy, not cosine-to-median) |
| \(K_A \ll K_H\) compression asymmetry | Compact structural drive vector vs human narrative mood |
| Pipeline compliance (invariant→model→code→countermodel) | Causal trace with typed pipeline stages |
| NAMM-2026-013 antigravity protocol | NammAdapter fires when epistemic+coherence thresholds met |
| AI thinking topology (004) | Meta-evaluator fixed-point arbitration among intention candidates |

BeliefField module docstring and DriveEngine explicitly reference this asymmetry — machine-native structural signal (K_A analog) vs unused human embedding space (K_H analog).

**Loop 3 / Loop 27:** `NammAdapter.run_sandbox("NAMM-2026-013")` is **runnable** when `NAMM_ROOT` points to a live install. Verified certificates propagate to `AuthenticReasonDiscriminator` as `namm_sandbox_verified` reason code (supplementary audit signal, not an endogeneity gate).

Experiments **008–010** remain adapter stubs — hooks fire at configured thresholds but no live CLI delegation until MVP-1 shadow mode ([`MVP1_SHADOW_PLAN.md`](./MVP1_SHADOW_PLAN.md)).

---

## 5. EIA dev-loop findings (Loops 12–23)

| Loop | Finding | NAMM relevance |
|------|---------|----------------|
| 12–18 | full_eia EUIR 100% vs reactive/P3 0% | Validates G2 before citing NAMM results externally |
| 15 | Main trace +7 audit nodes vs starter | sense_making, twin_run, eoi_score, authentic_reason decomposition |
| 8, 19 | κ=0.0 on user-heavy traces; precision 100% | SourceMass topology predicts but does not replace replay (H5) |
| 3, 27 | NAMM-013 sandbox verified locally | Certificate wired into AuthenticReason verdict payload |

---

## 6. Causal trace stage labels

Each pipeline stage emits a trace node with `pipeline_stage` field:

```
observation_ingest → sense_making → motive_formation → intention_genesis → initiative_emission → contact_governor
                              ↘ namm_hook (when thresholds met)
```

Run demo: `eia pipeline --scenario scenarios/pipeline_demo_002.yaml`

---

## 8. WoE v0.2 / EIS research branch hooks

Research track: [`research/cursor-starter-v0.2/`](../research/cursor-starter-v0.2/) on branch `research/cursor-starter-v0.2-woe-eis`. Sci-flow registry: [`research/sci_flow/config.yaml`](../research/sci_flow/config.yaml).

| WoE / EIS construct | NAMM experiment | Module | Notes |
|---------------------|-----------------|--------|-------|
| Kuramoto order parameter R | NAMM-2026-013, 014 | `kuramoto` (consensus_non_optimality) | Correlate with `coherence.py` R |
| Phase scramble (CF-5) | NAMM-2026-006 | `tda` (gudhi/ripser) | Topological falsifier for metastability claim |
| Denied WoE intents (CF-7) | NAMM-2026-001 | rejections.jsonl | Collider bias guard |
| EIS metadata on proposals | NAMM-2026-004 | meta_evaluation | Future `audit/eis.py` port (M-B) |
| Hz carrier factorial | NAMM-2026-014 | oscillation covariates | 20/30/42/70 Hz cells (M-F) |
| Cognitive class vs EIS | NAMM-2026-023 | cognitive_class + tda | CCT separation proxy |

Full library catalog: [`NAMM_SCI_LIBRARIES.md`](./NAMM_SCI_LIBRARIES.md).

---

## 7. Document history

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-08-17 | Initial crosswalk; Hz loop mapping; experiment hooks 001–007, 013–014 |
| 0.2 | 2026-08-17 | Added 008–010 stub status; NAMM-013 runnable + AuthenticReason cert wire; Loops 12–23 findings |
| 0.3 | 2026-08-18 | WoE v0.2 research branch; NAMM_SCI_LIBRARIES catalog; sci-flow cross-ref (kuramoto↔coherence, tda↔CF-5); experiments 021–029 |
