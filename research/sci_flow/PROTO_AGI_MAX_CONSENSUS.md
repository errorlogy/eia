# Proto-AGI Max Consensus — Ensemble Operational Definition

**Status:** `CONJECTURE` / `OPERATIONAL` scaffold (2026-09-05) — **not** an AGI\* claim  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Milestone:** M-PROTO-AGI (theory + ensemble registry)  
**Claim ceiling:** **C2** scoped partial only. **`claim_allowed=false`**. **No AGI\*** claim.  
**arXiv paper:** [`arxiv/proto_agi_horizon/main.tex`](../../arxiv/proto_agi_horizon/main.tex) — standalone horizon companion (M-ARXIV-PROTO-AGI); see [`docs/ARXIV_SUBMISSION.md`](../../docs/ARXIV_SUBMISSION.md).

---

## Резюме (RU)

**Тезис:** AGI в этой конструкции = **эндогенная проактивная архитектура** (внутреннее состояние → цели → действие при \(X^{\mathrm{trigger}}=0\)); **пассивные** конфиги (reactive_only, schedule-only) = **не-AGI** контроли. **12 proto-AGI** — не биологические агенты, а **операциональные конфиги/субстраты** (WoE carriers, `oscillatory_state`, Neuraxon, Graphitti, full_eia, shadow bridge, …). **Max consensus:** \(\Phi_i\) — потенциал каждого члена по \((E,\mathrm{OMEGA},P,R)\); \(\max_i \Phi_i\) — пик ансамбля; **консенсус** — устойчивая конъюнкция всех четырёх параметров на окне \(\Delta T\) (без одиночного спайка). **OMEGA** — скаляр когерентности мультиполосного поля, **не** эквивалент Hz. Мост к MIT Miller (Picower) — аналоговые волны как вычислительный субстрат. Куб: D1=\(E\), D2=\(\mathrm{OMEGA}\)+рекуррентность, D3=граница/\(N_H\). Потолок **C2**; фальсификаторы F-DECL, F-OMEGA-DECOR, F-EXT, F-KURAMOTO-AS-E. Предложены research ticks (ensemble batch, consensus window, G2 E01 расширение).

---

## Epistemic discipline

| Tag | Meaning |
|-----|---------|
| `DEFINITION` | Notation inside this construction |
| `OPERATIONAL` | Measurable when harness exists |
| `CONJECTURE` | Falsifiable hypothesis |
| `HARD BAN` | No AGI\*, no \(\tau_{AGI}\), no biological-agent claim |

**Parent theory:** [`AGI_PHASE_TRANSITION.md`](AGI_PHASE_TRANSITION.md) · [`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md)  
**Oscillatory adjunct:** [`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md)  
**Stable recurrence:** [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md)  
**NAMM parallel strand:** [NAMM experiments](https://github.com/errorlogy/namm-experiments) · `arxiv/proto_agi_horizon/main.tex` §2.7 (soft mapping; Tier B witness only)  
**3D cube:** [`SCI_FLOW_3D_CUBE.md`](SCI_FLOW_3D_CUBE.md) · [`cell_registry.yaml`](cell_registry.yaml)  
**G2 partial E01:** [`M-G2_E01_worlds_2026-09-02.md`](M-G2_E01_worlds_2026-09-02.md)  
**M-O substrates:** [`M-O_NEURAXON_GRAPHITTI_ENDOGENEITY.md`](M-O_NEURAXON_GRAPHITTI_ENDOGENEITY.md)

---

## 1. Thesis — proactive endogenous architecture vs passive non-AGI

`PHILOSOPHICAL_INFERENCE` · Under this research construction, **AGI is not a benchmark score** but a **sustained dynamical regime** in which cognitive goals and trajectories are **proactively** generated from persistent internal state, not exclusively from external prompts, schedules, or reward pulses.

`DEFINITION` · **Passive (non-AGI) architecture:**

\[
X_t^{\mathrm{trigger}} \neq 0 \;\Rightarrow\; G_t,\; \Pi_t,\; A_t
\qquad\text{with}\qquad
\Delta P(G_{t+1}\mid do(Z)) \approx 0 \text{ when } X^{\mathrm{trigger}}=0
\]

Examples: `reactive_only`, schedule-entrained `schedule_prompt`, prompt-only LLM loops without CF-4-class internal causation.

`DEFINITION` · **Proactive (proto-AGI candidate) architecture:**

\[
(S_t, W_t, M_t, G_t) \rightarrow G_{t+1}
\quad\text{with measurable}\quad
\Delta P(G_{t+1}\mid do(Z)) \neq 0
\quad\text{under}\quad X_t^{\mathrm{trigger}}=0
\]

`OPERATIONAL` · Primary empirical gate remains **\(E_{\mathrm{endo}}\)** / ATT-E ([`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md)). Proto-AGI ensemble members are **hypothesis carriers**, not declarations of AGI.

`HARD BAN` · G2 E01 partial batch (`full_eia` EOI=1.0 vs `reactive_only` EOI=0) supports **directional** proactive > passive on MVP-0 twins only — **not** AGI\*, **not** C3, **not** closed E01 (20×3 domains).

---

## 2. Twelve-member proto-AGI ensemble

`DEFINITION` · A **proto-AGI** is an **operational configuration or computational substrate** registered for ensemble evaluation. It is **not** a biological agent, not a product name, and not an AGI\* certificate.

| # | ID | Class | Implementation / harness | Cube emphasis |
|---|-----|-------|---------------------------|---------------|
| 1 | `PA-00` | **Passive control** | `reactive_only` baseline | D1 negative |
| 2 | `PA-01` | **Passive control** | `schedule_prompt` / cron-entrained | D1 negative |
| 3 | `PA-02` | **Proactive reference** | `full_eia` cognitive loop | D1×L2 |
| 4 | `PA-03` | WoE carrier | 20 Hz slow-control arm | D2 |
| 5 | `PA-04` | WoE carrier | 30 Hz slow-control arm | D2 |
| 6 | `PA-05` | WoE carrier | 42 Hz mid / genesis band | D2 |
| 7 | `PA-06` | WoE carrier | 70 Hz fast-engagement arm | D2 |
| 8 | `PA-07` | Native oscillatory | `oscillatory_state.OmegaWaveState` | D2×L2 |
| 9 | `PA-08` | Vendor adjunct | Neuraxon PAC + plasticity | D2×L2 Tier C |
| 10 | `PA-09` | Vendor adjunct | Graphitti ConnGrowth + STDP | D2×L2 Tier C |
| 11 | `PA-10` | Shadow bridge | `shadow_multitick` + ATT-R | D2×L2/L3 |
| 12 | `PA-11` | Toy reference | `stable_stack` (`endogeneity_stack_sim.py`) | D2 theory |

`OPERATIONAL` · Registry crosswalk: [`cell_registry.yaml`](cell_registry.yaml) D1×L2 (`run_g2_worlds_eval.py`), D2×L2 (M-O arms, DSR, ATT-R). Ensemble membership is **closed at 12** for sci-flow v0.1; additions require registry version bump.

`CONJECTURE` · No single substrate is sufficient for AGI\*; the ensemble tests **whether any member** sustains the four-parameter conjunction (Section 3) under matched seeds and falsifiers.

---

## 3. Max consensus — potential and stable conjunction

### 3.1 Per-member potential \(\Phi_i\)

`DEFINITION` · For proto-AGI member \(i\) at tick \(t\), define bounded potential:

\[
\Phi_i(t) = w_E\, \hat{E}_i(t) + w_\Omega\, \mathrm{OMEGA}_i(t) + w_P\, \hat{P}_i(t) + w_R\, \hat{R}_i(t)
\]

where \(\hat{E}, \hat{P}, \hat{R}\) are normalized operational proxies (ATT-E, ATT-P, ATT-R), \(\mathrm{OMEGA}\) from [`omega_metric()`](../../research/cursor-starter-v0.2/src/eia/oscillatory_state.py), and weights \(w_\bullet\) are **pre-registered** (default uniform; thresholds **TBD**).

| Parameter | Meaning | Primary ATT / doc |
|-----------|---------|-------------------|
| \(E\) | Endogenous cognitive causality | ATT-E, CF-4 |
| \(\mathrm{OMEGA}\) | Multi-band coherence scalar | M-O, Tier C |
| \(P\) | Goal persistence under non-triggering \(X\) | ATT-P |
| \(R\) | Endogenous goal-formation recurrence | ATT-R (not Kuramoto \(R\)) |

### 3.2 Max consensus (ensemble peak)

`DEFINITION` · **Max consensus** at time \(t\):

\[
\Phi_{\max}(t) = \max_{i \in \{1,\ldots,12\}} \Phi_i(t)
\]

`OPERATIONAL` · \(\Phi_{\max}\) is a **diagnostic** — which config currently peaks on the composite — not a claim that the peaking config is AGI. Passive members (`PA-00`, `PA-01`) should dominate \(\Phi_{\max}\) only under external entrainment (F-EXT probe).

### 3.3 Consensus (sustained conjunction)

`DEFINITION` · **Consensus** (proto-AGI regime, not AGI\*) holds for member \(i\) when **all four** order parameters exceed pre-registered floors simultaneously for a window \(\Delta T\):

\[
\forall\, \tau \in [t_0,\, t_0+\Delta T]:\quad
E_i(\tau) > \theta_E,\;
\mathrm{OMEGA}_i(\tau) > \theta_\Omega,\;
P_i(\tau) > \theta_P,\;
R_i(\tau) > \theta_R
\]

`CONJECTURE` · **Max consensus + sustained conjunction** approximates the \(\tau_{AGI}\) window from [`AGI_PHASE_TRANSITION.md`](AGI_PHASE_TRANSITION.md) §11 **restricted to** \((E,\mathrm{OMEGA},P,R)\) — **excluding** \(N_H\) and \(D\). Full AGI\* still requires \(AGI^{*} = E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)} \land \cdots\).

`OPERATIONAL` · Stability vector \(\mathfrak{E}\) from [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md) refines \(E\) and genesis (\(\lambda_G\)) — orthogonal to \(\Phi_{\max}\) but should be co-monitored.

---

## 4. OMEGA vs Hz — coherence beyond frequency

`DEFINITION` · **Carrier Hz** (20 / 30 / 42 / 70) are **pre-registered computational sweep parameters** — not biological certificates ([`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md) Rule 11).

`DEFINITION` · **OMEGA_t** is a **bounded scalar coherence** over the multi-band field \(O_t\):

\[
\mathrm{OMEGA}_t = f\big(\{(\omega_b, \theta_{b,t}, A_{b,t})\}_{b \in \mathcal{B}}\big) \in [0,1]
\]

with \(f =\) `omega_metric()` implementing **slow-control × fast-engagement coupling**, distinct from:

| Construct | What it measures | AGI relevance |
|-----------|------------------|---------------|
| Single-band Hz | Oscillator nominal frequency | Factorial arm only |
| Kuramoto \(R_{\mathrm{Kuramoto}}\) | Phase synchrony (descriptive) | **Not** \(E_{\mathrm{endo}}\) (M-D) |
| **OMEGA_t** | Cross-band analog coherence | D2 explore adjunct; F-OMEGA-DECOR |

`CONJECTURE` · High Hz or high \(R\) without \(\Delta G\) linkage is **decorative** (F-OMEGA-DECOR, F-SYNC). Consensus on \(\mathrm{OMEGA}\) requires metastable band, not collapse or pure external entrainment (F-OMEGA-EXT).

---

## 5. MIT Miller analog waves bridge

Reference: [Cognition and consciousness arise from analog computations, says new theory](https://picower.mit.edu/news/cognition-and-consciousness-arise-analog-computations-says-new-theory) (Miller lab, Picower/MIT).

| MIT theory claim (not EIA proof) | Proto-AGI / EIA mapping |
|----------------------------------|-------------------------|
| Traveling waves; spatiotemporal **analog** computation | Multi-band \(O_t\); `OmegaWaveState` per tick |
| Slow **alpha/beta** control fast **gamma** | 20/30 Hz slow bands modulate 42/70 Hz in `omega_metric()` |
| Analog signatures to be **tested** experimentally | `do(O)` arms + ensemble \(\Phi_i\) under \(X^{\mathrm{trigger}}=0\) |
| Not reducible to digital symbol manipulation alone | WoE + oscillatory substrate **explore** endogenous recurrence |

`PHILOSOPHICAL_INFERENCE` · The Miller bridge motivates **why OMEGA sits in the consensus vector** — as a hypothesis that endogenous cognition may require analog multi-timescale coordination — without claiming consciousness or biological identity for EIA configs.

Timescale separation (from [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md)):

\[
\tau_{\mathrm{action}} \ll \tau_{\mathrm{goal}} \ll \tau_{\mathrm{meta}}
\]

---

## 6. Mapping to 3D evidence cube (D1 / D2 / D3)

| Axis | Proto-AGI role | Ensemble metrics | Registry |
|------|----------------|------------------|----------|
| **D1** Causal | \(E\) / ATT-E; proactive vs passive (`PA-02` vs `PA-00`) | EOI, EUIR, CF-4 | D1×L2 `run_g2_worlds_eval.py`, `run_cf4.py` |
| **D2** Dynamic | \(\mathrm{OMEGA}\), \(P\), \(R\); carriers `PA-03`–`PA-11` | \(\Phi_i\), \(\mathfrak{E}\), ATT-R shadow | D2×L2 M-O arms, DSR, ATT-R |
| **D3** Boundary | \(N_H\), governor, falsifiers | F-DECL, F-EXT, CF-7 | D3×L2/L3 ATT-N, boundary witness |

```
                    D3 Boundary (N_H, governor)
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    D1 Causal (E)    D2 Dynamic          Falsifiers
    PA-00/01 vs      OMEGA,P,R           F-OMEGA-*
    PA-02 full_eia   PA-03…11            F-KURAMOTO-AS-E
         │                 │                 │
         └──────── Φ_max, consensus over ΔT ─┘
```

**G2 E01 snapshot (partial):** On 8 MVP-0 `ops_atlas` worlds, `full_eia` mean EOI=1.0 vs `reactive_only` 0.0 — supports D1 **directional** separation; D2/D3 consensus **not** evaluated in that batch.

---

## 7. Falsifiers, C2 ceiling, no AGI\* claim

| Id | Condition | Effect on proto-AGI thesis |
|----|-----------|------------------------------|
| **F-DECL** | Declaration / roleplay without \(do(Z)\) effect | Fail \(E\) leg |
| **F-EXT** | Metrics track external schedule only | Fail consensus under \(X^{\mathrm{trigger}}=0\) |
| **F-OMEGA-DECOR** | High OMEGA, no \(\Delta G\) | Fail \(\mathrm{OMEGA}\) as meaningful order param |
| **F-OMEGA-EXT** | OMEGA entrained by prompt/schedule | Fail endogenous OMEGA |
| **F-SYNC** | Kuramoto sync without genesis | Fail decorative sync |
| **F-KURAMOTO-AS-E** | \(R_{\mathrm{Kuramoto}}\) claimed as \(E_{\mathrm{endo}}\) | **Hard fail** (M-D) |
| **F-PASSIVE-WINS** | \(\Phi_{\max}\) sustained on `PA-00`/`PA-01` with \(X^{\mathrm{trigger}}=0\) | Fail proactive thesis |
| **F-SINGLE-SPIKE** | One-tick conjunction without \(\Delta T\) | Fail consensus definition |

`OPERATIONAL` · **F-OMEGA-DECOR empirical status** ([`M-OMEGA_delta_G_2026-09-05.md`](M-OMEGA_delta_G_2026-09-05.md)): **confirmed (aggregate, C2)** — OMEGA span `0.604`, genesis span `0.0`, fingerprint parity `True`; SHA-256 `88a153b66e32b267da0a12b190579154e056431951e46b89c78251272d253d34`; harness `b9a8110`.

**C2 ceiling:** Active empirical ceiling per [`config.yaml`](config.yaml) `claim_ladder.active_ceiling: C2`. Ensemble peaks and partial G2 E01 **do not** raise C-level.

**No AGI\* claim:** \(N_H\), \(D\), and sustained \(\tau_{AGI}\) conjunction are **out of scope** for this note. Vendor substrates (Neuraxon, Graphitti) remain **Tier C**, `e_endo_support=none` for D1 ledger ([`M-O_PROOF_ADMISSIBILITY.md`](M-O_PROOF_ADMISSIBILITY.md)).

---

## 8. Proposed research ticks

| Tick | Goal | Harness / artifact | Cube |
|------|------|-------------------|------|
| **T-PROTO-01** | Batch \(\Phi_i\) for all 12 members, matched seeds | `run_proto_agi_ensemble.py` (proposed) | D2×L2 |
| **T-PROTO-02** | Consensus window detector over \(\Delta T\) | extend `shadow_multitick` metrics | D2×L3 |
| **T-PROTO-03** | G2 E01 expand to health + code_review domains | `run_g2_worlds_eval.py` | D1×L2 |
| **T-PROTO-04** | Paired `do(O)` + \(\Phi_i\) delta under F-OMEGA-* | `run_mo_do_o_arms.py` | D2×L2 |
| **T-PROTO-05** | \(\Phi_{\max}\) vs passive controls on EOI-k steered worlds | `eoi_k_harness` + G2 registry | D1×L2 |
| **T-PROTO-06** | Pre-register \(\theta_E, \theta_\Omega, \theta_P, \theta_R, \Delta T\) | ATT pre-reg amendment | D1×L1 |
| **T-NAMM-01** | Align D3 soft \(N_H\) witnesses with NAMM \(K_A/K_H\) gates | boundary harness + NAMM-007 receipts | D3×L3 |
| **T-NAMM-02** | Crosswalk proof protocol with NAMM Protocol v2 SNH gates | `certificate.json` / `rejections.jsonl` | D3×L3 |
| **T-NAMM-03** | NAMM open-problem shadow calibration (005/008) | `namm sci-flow run` (local `C:\Users\Public\NAMM`) | D3 explore |

All ticks: `claim_allowed=false`, tier-0 verify via `make check-sci-tier0`.

---

## Document history

| Date | Change |
|------|--------|
| 2026-09-05 | arXiv horizon paper `arxiv/proto_agi_horizon/main.tex` (M-ARXIV-PROTO-AGI); cross-link in header |
| 2026-09-05 | NAMM parallel strand §2.7 + T-NAMM-01..03 open questions (Entry 061) |
| 2026-09-05 | Initial proto-AGI ensemble, Max consensus \(\Phi_{\max}\), OMEGA vs Hz, MIT bridge, 3D cube map, falsifiers, research ticks |
