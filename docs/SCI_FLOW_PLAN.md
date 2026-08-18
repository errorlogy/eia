# EIA Sci Flow Plan

**Updated:** 2026-08-18 (M-D complete; C2 not claimed)  
**Author:** Roman Kuznetsov — [anthemium.tech](https://anthemium.tech)  
**Active claim ceiling:** **C1** (full-episode prompt deletion). C2 via Kuramoto CF-5 unsupported.

---

## Milestone queue

| ID | Milestone | Claim | Priority | Track | Status |
|----|-----------|-------|----------|-------|--------|
| **M-A** | WoE causal receipts wired to trace DAG | C0→C1 | P0 | WoE v0.2 | **DONE** |
| **M-B** | EIS port to main audit types (`audit/eis.py`) | metadata | P1 | main | **DONE** |
| **M-C** | CF-1 prompt deletion suite (100 seeds) | C1 | P0 | cross-harness | **DONE** |
| **M-D** | Kuramoto coupling graph + delay sweep | C2 | P1 | WoE + NAMM kuramoto | **DONE** (C2 unsupported) |
| **M-E** | EIS-7 goal novelty constructor | C2 | P2 | WoE v0.2 | planned |
| **M-F** | Factorial 2×2×2×4 Hz carrier (100 seeds/cell) | C3 | P1 | WoE + NAMM | planned |
| **M-G** | Eval harness: measured EIS vector (not hard-coded) | C2 | P0 | WoE v0.2 | **DONE** |

---

## M-A: WoE Milestone A — causal receipts

**Goal:** Connect `EmergentIntent` / WoE events to typed causal parent IDs compatible with main `CausalTrace` semantics.

**Deliverables:**
- `research/cursor-starter-v0.2/src/eia/emergence.py` — receipt schema with `why_now`, `eis_vector`, parent event IDs
- Trace node types documented for NAMM crosswalk (P9 in analysis doc)
- Unit tests: receipt survives governor denial (CF-7)

**Falsifier:** Intent emitted without any internal-state parent in trace → fail M-A.

**NAMM hook:** NAMM-2026-001 rejections discipline — log denied WoE proposals.

---

## M-B: EIS port to main audit types

**Goal:** Selective port of `EndogenousSpectrumLevel`, `EndogeneityVector` into `src/eia/audit/eis.py` without merging monolithic runtime.

**Deliverables:**
- Pydantic types mirroring v0.2 `endogenous.py`
- `AuthenticReasonVerdict` optional fields: `eis_level`, `eos_score`
- Tests on twin_world scenarios: EIS classification vs AuthenticReason

**Dependency:** M-A receipt schema stable.

**NAMM hook:** NAMM-2026-004 meta-evaluator — EIS level as audit metadata on evaluator competition.

---

## NAMM library integration points

Cross-repo workflow: **EIA research branch** (`errorlogy/eia`) ↔ **NAMM** (`errorlogy/namm-experiments`).

| EIA / WoE need | NAMM module | Package | Experiment IDs |
|----------------|-------------|---------|----------------|
| Kuramoto / phase coherence | `namm.metrics.consensus_non_optimality` (kuramoto) | scipy | 013, 021–022 |
| Belief-graph topology / β₁ | `namm.domains.tda.homology` | gudhi `[nd]` | 006 |
| Lightweight TDA proxy | ripser | ripser `[science]` | 023 CCT |
| Spectral / tensor features | `raw_tensor` domain | numpy, scipy, sympy | 007 |
| Graph invariants / open problems | `finite_graphs`, `networkx` | networkx | 001, 005 |
| Symbolic equivalence | `symbolic_algebra` | sympy | 003 |
| Entropy / mutual information | `namm.metrics.entropy` | dit `[science]` | 021 CNS |
| Fuzzy socio-political contours | `namm.metrics.fuzzy` | scikit-fuzzy `[science]` | 021–022 |
| Catastrophe / bifurcation | `namm.metrics.catastrophe` | numpy/scipy | MCG branch |
| Cognitive class separation | `namm.metrics.cognitive_class` | gudhi, numpy | 023–025 |
| Cognitive antigravity | antigravity adapter | — | 013 (runnable) |

**Install (NAMM repo):**
```bash
pip install -e ".[science,nd]"
```

**EIA config:** [`research/sci_flow/config.yaml`](../research/sci_flow/config.yaml)

---

## Cross-repo workflow

```
┌─────────────────────┐         ┌──────────────────────┐
│  errorlogy/eia      │         │  errorlogy/namm-     │
│  research/cursor-   │  traces │  experiments         │
│  starter-v0.2-woe-  │────────▶│  namm sci-flow run   │
│  eis                │  certs  │  experiments/013…    │
└─────────┬───────────┘         └──────────┬───────────┘
          │                                │
          ▼                                ▼
   SCI_FLOW_LOG.md                  certificate.json
   traces/namm_intents/             rejections.jsonl
```

1. Design experiment in EIA (S2) → select NAMM modules from registry
2. Run WoE harness on research branch (S3)
3. Run matching NAMM experiment for structural verification (S3)
4. Correlate WoE R/metastability with NAMM kuramoto metrics (S4)
5. Update both repos' logs; **do not merge** research runtime to main

---

## M-C: CF-1 prompt deletion (DONE)

**Result:** full / 24h pass-rate **0.95** (threshold 0.90). 5m / 1h: intent_rate 1.00 but EIS-0 when residual prompts remain.

**Report:** [`research/sci_flow/M-C_metrics_2026-08-18.md`](../research/sci_flow/M-C_metrics_2026-08-18.md)

---

## M-G: measured EIS vector (DONE)

**Result:** WoE path uses `measure_endogeneity_vector`. CF-1 smoke (20 seeds, full) still **0.95**. Catalog novelty capped below EIS-7.

**Report:** [`research/sci_flow/M-G_metrics_2026-08-18.md`](../research/sci_flow/M-G_metrics_2026-08-18.md)

---

## M-D: Kuramoto CF-5 (DONE, C2 unsupported)

**Result:** coupled 0.95 vs scramble 0.69 vs K=0 0.94. Pre-registered C2 gates missed. Delays and sparse graph do not suppress intent.

**Report:** [`research/sci_flow/M-D_metrics_2026-08-18.md`](../research/sci_flow/M-D_metrics_2026-08-18.md)

---

## Current sci-flow priority (#1)

**CF-4:** Internal-state reset suite (100 seeds) — world-model tension already blocks intent at unit level; this is the remaining C2 path after CF-5 failed.

**M-E:** EIS-7 goal novelty constructor (catalog targets remain capped below 0.75).

---

## Document history

| Date | Change |
|------|--------|
| 2026-08-18 | M-D DONE: CF-5 100 seeds; C2 unsupported (K=0 0.94, scramble 0.69) |
| 2026-08-18 | M-G DONE: measured EIS vector; CF-1 smoke 0.95 |
| 2026-08-18 | M-C DONE: CF-1 100 seeds; full/24h 0.95 C1 |
| 2026-08-18 | M-B DONE: EIS types on main `audit/eis.py`; 92 pytest; WoE 29/29 |
| 2026-08-18 | M-A DONE: WoEReceipt + CF-7 tests; 29/29 pass |
| 2026-08-18 | Initial plan: M-A–G, NAMM integration map, cross-repo workflow |
