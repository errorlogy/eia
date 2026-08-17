# NAMM ↔ EIA Pipeline Artifact Crosswalk

**Status:** v0.1 research mapping  
**Author:** Roman Kuznetsov — [anthemium.tech](https://anthemium.tech)  
**Date:** August 17, 2026

Maps the EIA cognitive pipeline (`observation → comprehension → motive → intention → initiative`) to NAMM verification artifacts, experiments, and Hz-band analogies from the `hypothesis/cognitive-antigravity` branch.

**Related:** [`NAMM_INTEGRATION.md`](./NAMM_INTEGRATION.md) · NAMM [`docs/BRAINWAVE_OSCILLATION_HYPOTHESIS.md`](https://github.com/errorlogy/namm-experiments/blob/main/docs/BRAINWAVE_OSCILLATION_HYPOTHESIS.md) · [`docs/AI_THINKING_TOPOLOGY.md`](https://github.com/errorlogy/namm-experiments/blob/main/docs/AI_THINKING_TOPOLOGY.md) · [`docs/COGNITIVE_ANTIGRAVITY_HYPOTHESIS.md`](https://github.com/errorlogy/namm-experiments/blob/main/docs/COGNITIVE_ANTIGRAVITY_HYPOTHESIS.md)

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
| NAMM-2026-013 | `meta_evaluation` | MotiveFormation | Cognitive antigravity v1 (H-CA-001) |
| NAMM-2026-014 | oscillation covariates | Reflection (L-L) | Ω_c / band-coherence vs 013 arms |

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

---

## 5. Causal trace stage labels

Each pipeline stage emits a trace node with `pipeline_stage` field:

```
observation_ingest → sense_making → motive_formation → intention_genesis → initiative_emission → contact_governor
                              ↘ namm_hook (when thresholds met)
```

Run demo: `eia pipeline --scenario scenarios/pipeline_demo_002.yaml`

---

## 6. Document history

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-08-17 | Initial crosswalk; Hz loop mapping; experiment hooks 001–007, 013–014 |
