# NAMM Scientific Libraries — EIA / WoE Research Catalog

**Status:** v0.1 — August 18, 2026  
**Author:** Roman Kuznetsov — [anthemium.tech](https://anthemium.tech)  
**Source repo:** [errorlogy/namm-experiments](https://github.com/errorlogy/namm-experiments) (local: `c:\Users\Public\NAMM`)

Maps NAMM's scientific Python stack to EIA main pipeline, EIS/WoE v0.2 research branch, and sci-flow experiment registry.

**Related:** NAMM [`docs/SCIENTIFIC_STACK.md`](https://github.com/errorlogy/namm-experiments/blob/main/docs/SCIENTIFIC_STACK.md) · [`docs/NAMM_DOMAIN_UNIVERSE.md`](https://github.com/errorlogy/namm-experiments/blob/main/docs/NAMM_DOMAIN_UNIVERSE.md) · EIA [`SCI_FLOW_PLAN.md`](SCI_FLOW_PLAN.md) · [`NAMM_ARTIFACT_CROSSWALK.md`](NAMM_ARTIFACT_CROSSWALK.md)

---

## Install profiles

| Profile | Command | Use in EIA/WoE research |
|---------|---------|-------------------------|
| Core | `pip install -e .` | networkx, sympy, numpy, scipy, z3, optuna — always available |
| Science | `pip install -e ".[science]"` | dit, scikit-fuzzy, ripser, nolds — entropy, fuzzy, lightweight TDA |
| ND | `pip install -e ".[nd]"` | gudhi, qutip — persistent homology, quantum stubs |
| Full | `pip install -e ".[dev,nd,science]"` | Complete sci-flow + pytest |

---

## Core dependencies (always installed)

| Library | Version | NAMM domains | EIA / WoE use |
|---------|---------|--------------|---------------|
| **networkx** | ≥3.2 | `finite_graphs`, `program_ast`, `open_problem_shadow`, `tda_frame` input graphs | Belief-graph topology; open-problem shadows; coupling graph for Kuramoto |
| **sympy** | ≥1.12 | `symbolic_algebra`, `program_ast`, `raw_tensor` | AST↔SymPy equivalence; symbolic sanity checks on WoE activation energy |
| **numpy** | ≥1.26 | all tensor/graph domains | Coherence field arrays; EIS vector storage |
| **scipy** | ≥1.11 | `raw_tensor`, `multi_agent_consensus`, Kuramoto ODE | **WoE Kuramoto** (`coherence.py`); opinion dynamics; spectral features |
| **z3-solver** | ≥4.12 | constraint domains | Formal checks on governor policies (future) |
| **optuna** | ≥3.5 | hyperparameter search | Seed sweep orchestration for factorial designs |

---

## Optional `[science]` extras

| Library | NAMM module | EIA / WoE use |
|---------|-------------|---------------|
| **dit** | `namm.metrics.entropy` | Shannon entropy, mutual information on belief distributions — CNS/CCT experiments |
| **scikit-fuzzy** | `namm.metrics.fuzzy` | Fuzzy membership for socio-political contours; governor threshold fuzzification (research) |
| **ripser** | TDA β₁ proxies | Lightweight persistent homology without full gudhi — fast WoE phase-scramble falsifiers |
| **nolds** | `namm.metrics.catastrophe` (Lyapunov) | Metastability detection; DFA on WoE timing series |

---

## Optional `[nd]` extras

| Library | NAMM module | EIA / WoE use |
|---------|-------------|---------------|
| **gudhi** | `namm.domains.tda.homology` | Persistent homology on belief-graph geodesic metric (NAMM-006) — SenseMaking stage |
| **qutip** | quantum stubs | Not used in WoE v0.2; reserved for future tensor invariants |

---

## In-repo NAMM metric modules (no PyPI extra)

| Module | Domains | EIA / WoE integration |
|--------|---------|----------------------|
| `namm.metrics.entropy` | information_theory, CNS | Belief update entropy; pairs with EIS-5 epistemic telogenesis |
| `namm.metrics.fuzzy` | fuzzy_logic, CNS | Contour membership — antigravity escape from median attractor |
| `namm.metrics.catastrophe` | catastrophe_theory | Thom fold/cusp/swallowtail — pure numpy/scipy; WoE metastability analog |
| `namm.metrics.consensus_non_optimality` | CNS, kuramoto | **Primary WoE bridge** — Kuramoto order parameter R vs EIA `coherence.py` |
| `namm.metrics.cognitive_class` | CCT | K0–K7 class separation; TDA on embedding trajectories |
| `namm.domains.tda.homology` | `tda_frame` | β₀, β₁ on belief contradictions — SenseMaking NAMM hook |

**Note:** Catastrophe theory has no maintained `pycatastrophe` on PyPI; NAMM implements potentials in pure numpy/scipy.

---

## Experiment → EIA stage mapping

| Experiment | Domain | Sci modules | EIA hook | WoE v0.2 hook |
|------------|--------|-------------|----------|---------------|
| NAMM-2026-001 | finite_graphs | — | InitiativeEmission null calibration | Rejections discipline for denied WoE intents |
| NAMM-2026-003 | program_ast | sympy, networkx | MotiveFormation epistemic sandbox | — |
| NAMM-2026-004 | meta_evaluation | — | IntentionGenesis evaluator competition | EIS metadata on competing proposals |
| NAMM-2026-006 | tda_frame | gudhi/ripser | SenseMaking β₁ tension | Phase organization falsifier (CF-5) |
| NAMM-2026-007 | raw_tensor | numpy, scipy, sympy | IntentionGenesis tensor invariants | Spectral features on coherence field |
| NAMM-2026-013 | meta_evaluation | kuramoto, antigravity | MotiveFormation H-CA-001 | **Kuramoto R** correlation with WoE R |
| NAMM-2026-014 | oscillation | kuramoto | Reflection L-L | Hz carrier factorial (20/30/42/70) |
| NAMM-2026-021–022 | multi_agent_consensus | entropy, fuzzy, consensus, kuramoto | — | Opinion dynamics baseline vs WoE |
| NAMM-2026-023–025 | cognitive_class_taxonomy | cognitive_class, tda, entropy | SenseMaking class separation | EIS level vs cognitive class proxy |

---

## Sci-flow CLI (NAMM side)

```bash
namm sci-flow run --experiment NAMM-2026-013
namm sci-flow run --experiment NAMM-2026-023
```

Registry: NAMM `data/sci_flow_registry.yaml`  
EIA mirror: [`research/sci_flow/config.yaml`](../research/sci_flow/config.yaml)

---

## Recommended pairing for WoE Milestone A–G

| Milestone | NAMM modules to run | Metric to correlate |
|-----------|---------------------|---------------------|
| M-A receipts | 001 (rejections) | denied proposal rate |
| M-D coupling | 013, kuramoto | R, metastability index |
| M-F Hz factorial | 014 | band-coherence vs carrier frequency |
| M-G measured EIS | 004, 023 | evaluator fixed points vs EIS vector |

---

## Document history

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-08-18 | Initial catalog from NAMM pyproject.toml + SCIENTIFIC_STACK.md |
