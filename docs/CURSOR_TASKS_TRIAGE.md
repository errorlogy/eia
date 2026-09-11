# CURSOR_TASKS — Triage (Sci-Flow vs Main)

**Дата:** 2026-09-01  
**Ветка sci-flow:** `research/cursor-starter-v0.2-woe-eis`  
**Потолок claim:** **C2** (scoped \(E_{\mathrm{endo}}\) / ATT-E partial). **Без AGI\*.**  
**Источники:** [`CURSOR_TASKS.md`](CURSOR_TASKS.md) · [`cursor_tasks.json`](cursor_tasks.json) · [`CURSOR_TASKS_SCI_FLOW_CROSSWALK.md`](CURSOR_TASKS_SCI_FLOW_CROSSWALK.md) · [`ENDOGENEITY_IMPLEMENTATION_PLAN.md`](ENDOGENEITY_IMPLEMENTATION_PLAN.md) · [`NEXT_SCI_AGENT_PROMPT.md`](NEXT_SCI_AGENT_PROMPT.md)

**Путь backlog:** интегрирован в `docs/` (корневой `CURSOR_TASKS.*` не используется).

---

## 1. Берём в работу СЕЙЧАС (research branch, sci-flow)

Приоритет для совместной работы на `research/cursor-starter-v0.2-woe-eis`. Tier 0 default; после каждого тика — `make check-sci-tier0`.

| # | ID | Задача | Почему сейчас | M-CLI / milestone |
|---|-----|--------|---------------|-------------------|
| 1 | **E04** | Longitudinal 50 ticks (DSR + EOI drift) | **Phase 2** — DSR **done** shadow; EOI drift open | M-E04-D05 · ATT-R |
| 2 | **D05** | DSR — 50 ticks, `d>0.3` persistence | **PASS** shadow carryover (seed 0); live daemon open | M-SE · `run_dsr_carryover.py` |
| 3 | *(sci)* | **Phase 2 daemon carryover** (`W'→G'` cross-tick) | Priority #1 в NEXT_SCI_AGENT_PROMPT; shadow-first, `emit_m0=false` | Phase 2 (нет Hermes ID) |
| 4 | **D01** | EOI-k (k=1,5,20) twin sweep | ATT-E / pool Tier A `E_ENDO`; интерпретация под `do(o=∅)` | M-CF4 · ATT-E |
| 5 | **B01** | Drive ablation 3×2 | Cross-check `loop_max_123` vs M-SE stack sim ablation | M-SE |
| 6 | *(pool)* | Metrics pool tick — Tier A/B (`E_ENDO`, `LAMBDA_G`, `P_G`) | M-EMP registry; один metric/tick в `/loop` | M-EMP |
| 7 | *(sci)* | **M-O** — OMEGA_t / `do(O)` shadow arm | `in_progress`; Tier C explore; falsifiers F-SYNC/F-KURAMOTO-AS-E | M-O |
| 8 | **H01** | CI gates (research half) | `eia-sci-tier0.yml` + tier-0 lock; не путать с main pytest | Phase 0 |
| 9 | **E05** | Multi-seed determinism (5 seeds) | Регрессия ATT runners перед Phase 2 merge | Phase 0 |
| 10 | **F01** | NAMM hermetic harness (optional) | T_NAMM_cert — **soft** ATT-N witness only; не strong \(N_H\) | T_NAMM_cert |

**Следующий конкретный шаг:** live daemon StateStore carryover **или** pool tick Tier A (**D01** / `E_ENDO`); E04 EOI drift deferred.

---

## 2. Берём на MAIN stack (production EIA)

Отдельный трек на `main` / `src/eia/` — Governor, drives, audit, eval, constitution. **Не мержить WoE runtime в main.**

| ID | Задача | Pri | Зачем |
|----|--------|-----|-------|
| **B05** | No-LLM-mood test | P0 | M-CLI Tier 0: drives ≠ embedding/LLM; тест ещё не создан |
| **C02** | V2 soft-defer freeze | P0 | Production AuthenticReason gate; 7/7 ADV |
| **C01** | ROC calibration (30 labels) | P0 | Замена magic 0.18; не для ATT C-ladder |
| **C03** | Taint tracking | P0 | Provenance → instruction block |
| **D02** | SA Source Autonomy | P0 | EIS audit (M-B); `SA>0.7` |
| **D04** | AP Abstain Precision | P0 | Human labels defer correct |
| **D09** | Threshold harmonization | P0 | Twin policies crosswalk |
| **E01** | 20 worlds × 3 domains | P0 | G2 eval worlds + human labels |
| **E02** | Held-out ADV-H1-H6 | P0 | Frozen adversarial harness |
| **E10** | G2 gate update | P0 | V2 + NAMM evidence pack |
| **H01** | CI gates (main half) | P0 | GitHub Actions EOI>0.7 |
| **H03** | Schemas frozen + ajv | P1 | JSON schema CI |
| **H05** | .env.example + gitleaks | P1 | Secret hygiene |
| **A04** | Pearl DAG for EOI | P0 | Causal narrative; figure для theory (можно параллельно main) |
| **A08** | Lexicographic policy proof | P1 | Ring 3>2>1 invariant test |
| **B02** | BeliefField gradients | P1 | `gradient_snapshot()` mapping |
| **B08** | Drive budget coupling | P1 | `r_t` inhibits `d` |
| **C04–C08** | Governor engineering | P1 | Fatigue, budget, trajectory risk, independence |
| **C10** | Governor sweep harness | P1 | Threshold sweep 0.05–0.30 |
| **D03, D06, D07, D10** | Explore metrics | P1 | AG, CE, CD, EUIR — не Tier A pool |
| **E03, E07, E09** | Baselines + protocol | P1 | ReAct, human eval, threats checklist |
| **F02, F05** | NAMM .vault + drive config | P1 | Compression hygiene |

**Main не блокирует sci-flow**, но **B05** и **C02** — trust foundation для production gate.

---

## 3. НЕ берём / HARD NO

Конфликтует с sci-flow policy, causal bar или branch isolation.

| Что | Hermes / phase | Почему NO |
|-----|----------------|-----------|
| **Merge WoE → main `src/eia/`** | — | Hard stop (NEXT_SCI_AGENT_PROMPT, eia-sci-flow skill) |
| **Kuramoto-as-\(E_{\mathrm{endo}}\) / ATT-R** | M-D falsified | coupled 0.95 ≈ K=0 0.94; F-KURAMOTO-AS-E |
| **Governor gutting** (`min_contact_score` down for science) | C02 inverse | Smoke ≠ evidence; M-R-LIVE flags |
| **AGI\* / \(\tau_{AGI}\) claims** | любой ATT partial | Ceiling C2; AGI\* = research horizon |
| **C2 re-claim via Kuramoto or M0 alone** | M-D, M-M0 | Pre-registered ban |
| **C3 from ATT-G/P/R explore alone** | M-E, M-P, M-R | `claim_allowed=false` |
| **C5 from ATT-D explore alone** | M-D2 | `c5_claim=false` |
| **Strong \(N_H\) from opacity / ATT-N** | M-N | explore proxy only |
| **Chat «I am endogenous» as \(E_{\mathrm{endo}}\)** | F-DECL | Declaration ≠ causation |
| **LLM every tick for goals** | Phase 4 misuse | ATT-G random_wording falsifier |
| **Telegram SEND as proof** | Phase 6 misuse | T_LIVE_gate witness only |
| **Prompt-as-drive** | CF-1 territory | F-EXT |
| **Paste AMAT JSON as bot persona** | M-M0 | Architecture harness only |

---

## 4. ОТЛОЖИТЬ (Phase 4+ / после закрытия science gaps)

| ID / phase | Задача | Отложить до |
|------------|--------|-------------|
| **G01–G04** | Hermes runtime bridge (SQLite, Governor, BeliefField, twin) | Phase 4+; external Hermes; не sci-flow merge |
| **G05** | P4→P5 bridge doc | После стабильного Phase 2 + main governor trust |
| **I01–I10** | arXiv, G2 pack, figures, release | Science gaps closed (carryover, DSR, pool Tier A bar) |
| **H02** | Docker repro one-liner | После tier-0 + main CI green |
| **Phase 4** | Tier 1 CLI genesis | `model_roles.enabled: true`; explore only |
| **Phase 5** | M-CLI metrics report | После Phase 4 |
| **Phase 6** | Telegram live witness | Последним; Phase 2 prerequisite |
| **F03, F04** | Trace manifold UMAP / compression conjecture | Paper polish |
| **A07, A09, I07, I08, I10** | P2 polish | Post-v0.2 |
| **B09** | Health `h_t` embodied | Future embodied |
| **E06, E08** | Cross-domain transfer, collider bias | Post G2 worlds |
| **H04** | OTEL traces | Infra nice-to-have |

---

## 5. УЖЕ СДЕЛАНО / частично

| Milestone | Status | Hermes overlap | Artifact |
|-----------|--------|------------------|----------|
| **M-A** | DONE | CF-2 scheduler null | WoE causal receipts |
| **M-B** | DONE | D02 partial, D08 legacy | EIS port main audit |
| **M-C** | DONE | CF-1 | `run_cf1.py` C1 0.95 |
| **M-CF4** | DONE | **D01** partial | C2 claimed (`zero_epistemic_gap` 0.06) |
| **M-G** | DONE | — | Measured EIS vector |
| **M-D** | DONE (falsified) | Kuramoto **≠ E** | coupled/scramble/k0 |
| **M-M0** | DONE | — | T_AMAT_M0 harness |
| **M-E** | DONE explore | ATT-G proxy | goal genesis falsifiers 0.0 |
| **M-P** | DONE explore | ATT-P proxy | persistence k∈{10,50,200} |
| **M-R** | DONE explore | ATT-R proxy | closed loop 1.0 |
| **M-R-LIVE** | DONE | **E04** prerequisite | shadow multitick; gap vs daemon documented |
| **M-N** | DONE explore | ATT-N proxy | `n_h_claim=false` |
| **M-D2** | DONE explore | ATT-D proxy | cross-domain 0.95 |
| **M-SE** | DONE | **D05** theory base | `STABLE_ENDOGENEITY.md` + stack sim |
| **M-CLI** | DONE | **B05** policy (test pending main) | Phase 0–1; `model_roles.py` |
| **M-EMP** | DONE | pool registry | Tier A–E + YAML + loader |
| **M-O** | **IN PROGRESS** | no 1:1 Hermes task | OMEGA_t, `oscillatory_state.py` |
| **Phase 0** | DONE | H01 research | `make check-sci-tier0` |
| **Phase 1** | DONE | B05 scaffold | ModelRoleAdapter stub |
| **Phase 3** | **PARTIAL** | A02/A03 theory | `THEORY_TZ_STABLE_ENDOGENEITY.md` |
| **Phase 2** | **NOT STARTED** | **E04, D05** | Daemon carryover — next |

**Hermes tasks partially covered by milestones:** D01 (CF-4 done, k-sweep open), D05 (toy sim done, 50-tick production open), B01 (stack sim ablation exists, loop_max matrix open), B05 (policy in config, **test missing on main**).

---

## 6. Decision matrix

| Task ID | Verdict | Why | Branch |
|---------|---------|-----|--------|
| A01 | MAIN | Pydantic AgentState; production schemas | main |
| A02 | DEFER | arXiv Sec.2.1; после science core | main |
| A03 | DEFER | arXiv Sec.2.2; после science core | main |
| A04 | MAIN | Pearl DAG; causal narrative (parallel OK) | main |
| A05 | MAIN | topology.py RI/ITD stub | main |
| A06 | DEFER | Related Work paragraph | main |
| A07 | DEFER | P2 polish | main |
| A08 | MAIN | Lexicographic invariant test | main |
| A09 | DEFER | P2 epistemic table | main |
| A10 | MAIN | EOI equivalence relation test | main |
| B01 | NOW | M-SE ablation cross-check | research + main |
| B02 | MAIN | BeliefField gradients | main |
| B03 | DEFER | Decay sweep; M-O params adjunct | main |
| B04 | DEFER | Saturation plot docs | main |
| B05 | MAIN | **P0 gap** — no test file yet; M-CLI Tier 0 lock | main |
| B06 | DEFER | P2 novelty source | main |
| B07 | MAIN | Governor↔drive coupling | main |
| B08 | MAIN | Drive budget invariant | main |
| B09 | DEFER | Embodied future | main |
| B10 | DEFER | Docs table; post calibration | main |
| C01 | MAIN | ROC calibration production gate | main |
| C02 | MAIN | V2 soft-defer production freeze | main |
| C03 | MAIN | Taint provenance P0 | main |
| C04 | MAIN | Quiet hours + fatigue | main |
| C05 | MAIN | Budget consumable | main |
| C06 | MAIN | Trajectory risk | main |
| C07 | DEFER | P2 consent race | main |
| C08 | MAIN | Independent governance test | main |
| C09 | DEFER | P2 sensor cascade | main |
| C10 | MAIN | Governor sweep harness | main |
| D01 | NOW | ATT-E / EOI-k; research interpretation | research + main |
| D02 | MAIN | SA metric P0 | main |
| D03 | MAIN | AG explore P1 | main |
| D04 | MAIN | AP human labels P0 | main |
| D05 | DONE-shadow | DSR / M-SE B_D; shadow carryover pass | research |
| D06 | MAIN | CE metric P1 | main |
| D07 | MAIN | CD norm P1 | main |
| D08 | NOW | κ study; M-B legacy formalize | research + main |
| D09 | MAIN | Threshold harmonization P0 | main |
| D10 | MAIN | EUIR formal P1 | main |
| E01 | MAIN | 20 worlds G2 P0 | main |
| E02 | MAIN | ADV held-out P0 | main |
| E03 | MAIN | ReAct baseline P1 | main |
| E04 | DONE-partial | DSR done shadow; EOI drift open | research |
| E05 | NOW | Determinism before carryover | research |
| E06 | DEFER | Cross-domain post G2 | main |
| E07 | MAIN | Human eval protocol | main |
| E08 | DEFER | Collider bias P2 | main |
| E09 | MAIN | Threats checklist | main |
| E10 | MAIN | G2 gate refresh P0 | main |
| F01 | NOW | T_NAMM soft witness (optional) | research + main |
| F02 | MAIN | .vault gitignore | main |
| F03 | DEFER | UMAP paper explore | main |
| F04 | DEFER | Compression conjecture | main |
| F05 | MAIN | NAMM drive config | main |
| G01 | DEFER | Hermes SQLite; Phase 4+ | external |
| G02 | DEFER | Hermes Governor; Phase 4+ | external |
| G03 | DEFER | Hermes BeliefField; Phase 4+ | external |
| G04 | DEFER | Hermes twin EOI; Phase 4+ | external |
| G05 | DEFER | Bridge doc; after Phase 2 | docs |
| H01 | NOW+MAIN | CI both tracks | both |
| H02 | DEFER | Docker after science gaps | main |
| H03 | MAIN | Schema ajv CI | main |
| H04 | DEFER | OTEL P2 | main |
| H05 | MAIN | gitleaks hygiene | main |
| I01 | DEFER | arXiv until gaps closed | main |
| I02 | DEFER | G2 pack; ties E10 | main |
| I03 | DEFER | Threat model complete | main |
| I04 | DEFER | Citations | main |
| I05 | DEFER | Figures batch | main |
| I06 | DEFER | README banner | main |
| I07 | DEFER | Changelog P2 | main |
| I08 | DEFER | License headers P2 | main |
| I09 | DEFER | Cursor rules glossary | main |
| I10 | DEFER | Release tag | main |
| *(sci)* Phase 2 | NOW | Daemon carryover W'→G' | research |
| *(sci)* M-O | NOW | OMEGA Tier C explore | research |
| *(pool)* Tier A/B | NOW | M-EMP loop ticks | research |

---

## Связанные документы

| Doc | Role |
|-----|------|
| [`CURSOR_TASKS_SCI_FLOW_CROSSWALK.md`](CURSOR_TASKS_SCI_FLOW_CROSSWALK.md) | ID-level mapping Hermes ↔ ATT/M-CLI |
| [`ENDOGENEITY_IMPLEMENTATION_PLAN.md`](ENDOGENEITY_IMPLEMENTATION_PLAN.md) | Phases 0–6 roadmap |
| [`NEXT_SCI_AGENT_PROMPT.md`](NEXT_SCI_AGENT_PROMPT.md) | Agent handoff + stop rules |
| [`.cursor/skills/eia-sci-flow/SKILL.md`](../.cursor/skills/eia-sci-flow/SKILL.md) | Branch policy |

---

## Document history

| Date | Change |
|------|--------|
| 2026-09-01 | Initial triage: NOW/MAIN/DEFER/NO/DONE matrix for 75 Hermes tasks + sci-flow phases |
