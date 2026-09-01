# Endogeneity Metrics Pool — Canonical Registry

**Status:** `OPERATIONAL` registry / `CONJECTURE` composites (2026-08-28) — **not** an AGI\* claim  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Milestone:** M-EMP (Endogeneity Metrics Pool)  
**Machine-readable:** [`endogeneity_metrics.yaml`](endogeneity_metrics.yaml)  
**Harness loader:** `research/cursor-starter-v0.2/src/eia/endogeneity_metrics.py`  
**Proof protocol:** [`EIA_PROOF_PROTOCOL.md`](EIA_PROOF_PROTOCOL.md) / `research/cursor-starter-v0.2/src/eia/evidence_proofs.py`  
**Claim ceiling:** **C2** scoped partial on \(E_{\mathrm{endo}}\) only

---

## Резюме (RU)

**Пул метрик эндогенности** — единый реестр порядковых параметров и прокси для sci-flow исследования перехода к AGI\* под конструкцией EIA. **Tier A:** \(E_{\mathrm{endo}}\) / \(E_C\) остаётся **PRIMARY** (ATT-E, CF-4). **Tier B:** компоненты вектора устойчивости \(\mathfrak{E}\). **Tier C:** OMEGA_t, \(O_t\), Kuramoto \(R\) — **только explore**, не Tier A. **Tier D:** \(N_H\), \(R\), \(D\) для горизонта AGI\* — research, не claimable. **Tier E:** ложные сигналы (declaration, sync-only, noisy-TV, entrainment). **ERI** — взвешенный дашборд (**CONJECTURE**), не доказательство AGI\*. Использовать в `/loop`: каждый тик — одна метрика Tier A/B с tier-0 verify; не повышать C-ladder без pre-registration.

---

## Epistemic discipline

| Tag | Meaning |
|-----|---------|
| `DEFINITION` | Notation / construct naming |
| `OPERATIONAL` | Instrumented or planned harness |
| `CONJECTURE` | Falsifiable hypothesis; thresholds TBD |
| `HARD BAN` | No AGI\* / \(\tau_{AGI}\) auto-claim from pool alone |

**Primary bar:** [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) — \(do(Z)\) under non-triggering \(X\).  
**ATT map:** [`AGI_TRANSITION_TEST.md`](AGI_TRANSITION_TEST.md)  
**Phase transition:** [`AGI_PHASE_TRANSITION.md`](AGI_PHASE_TRANSITION.md) · [`AGI_STAR_CRITERION.md`](AGI_STAR_CRITERION.md)  
**Stable endogeneity:** [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md)

---

## Tier overview

| Tier | Role | AGI\* claim? |
|------|------|--------------|
| **A** | Primary order parameters — transition detection | Partial C2 on \(E_{\mathrm{endo}}\) only |
| **B** | Stability vector \(\mathfrak{E}\) — metastable endogenous regime | No |
| **C** | Supporting substrates (oscillatory) — explore adjunct | No; **not** Tier A |
| **D** | AGI\* horizon conjunction legs — research | No |
| **E** | Falsifiers / non-metrics — what looks like endogeneity but isn't | N/A |
| **Composite** | ERI dashboard — weighted synthesis | **CONJECTURE** only |

---

## Tier A — Primary order parameters (transition detection)

Lead suite: **ATT-E**. \(E_{\mathrm{endo}}\) remains **PRIMARY**; operational proxies support but do not replace causal bar.

| id | symbol | definition | harness | ATT | threshold | status | claim_allowed |
|----|--------|------------|---------|-----|-----------|--------|---------------|
| `E_ENDO` | \(E_{\mathrm{endo}}\) | Endogenous cognitive causality: internal-state-driven goal formation / research / dynamics | `eia.cf4`, `run_cf4.py` | ATT-E | TBD | partial_c2 | **partial** |
| `E_C` | \(E_C\) | \(C_{\mathrm{int}}/(C_{\mathrm{int}}+C_{\mathrm{ext}})\) via \(do(Z)\) | `eia.causal` | ATT-E | TBD | proxy | false |
| `C_INT` | \(C_{\mathrm{int}}\) | Internal intervention divergence on \(P(G_{t+1}\mid do(Z))\) | `eia.causal` | ATT-E | TBD | proxy | false |
| `C_EXT` | \(C_{\mathrm{ext}}\) | External initiating-signal causal influence | `eia.causal` | ATT-E | TBD | proxy | false |
| `CF4_E_PARTIAL` | `e_endo_partial` | CF-4 discrete proxy: named internal factor suppression | `run_cf4.py` | ATT-E | discrete | partial_c2 | **partial** |

---

## Tier B — Stability vector \(\mathfrak{E}\) components

From [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md) §4. Map to ATT cells and drive-field harness.

| id | symbol | definition | harness | ATT | threshold | status | claim_allowed |
|----|--------|------------|---------|-----|-----------|--------|---------------|
| `LAMBDA_G` | \(\lambda_G\) | Goal birth rate (genesis events / tick) | `eia.goal_genesis`, M-E | ATT-G | TBD | explore | false |
| `P_G` | \(P_G\) | Temporal persistence under non-triggering \(X\) | `eia.goal_persistence`, M-P | ATT-P | TBD | explore | false |
| `Q_L` | \(Q_L\) | Learning productivity per internal episode | `endogeneity_stack_sim.py` | — | TBD | toy_sim | false |
| `H_G` | \(H_G\) | Goal diversity (entropy; noisy-TV guard) | stack sim / ATT-G | ATT-G | TBD | explore | false |
| `B_D` | \(B_D\) | Bounded drive norm \(\|d_t\|\in[d_{\min},d_{\max}]\) | `shadow_multitick.run_dsr_longitudinal_session`, stack sim | — | >0.3 persistence (D05 explore) | shadow_carryover | false |

---

## Tier C — Supporting substrates (explore only)

**Explicitly NOT Tier A.** High OMEGA_t or Kuramoto \(R\) without ATT-E / genesis linkage ⇒ decorative.

| id | symbol | definition | harness | ATT | threshold | status | claim_allowed |
|----|--------|------------|---------|-----|-----------|--------|---------------|
| `OMEGA_T` | \(\mathrm{OMEGA}_t\) | Multi-band analog wave scalar from \(O_t\) | `oscillatory_state.omega_metric()` | — | TBD | explore | false |
| `O_T` | \(O_t\) | Oscillatory internal field; \(\Psi(O_t)\to\Phi_t\to d_t\) | `oscillatory_state.py` | — | TBD | explore | false |
| `KURAMOTO_R` | \(R_{\mathrm{Kuramoto}}\) | Phase synchrony (descriptive); **≠** ATT-R \(R\) | `oscillatory_state.py` | — | — | falsified_necessity | false |

See [`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md), [`OSCILLATORY_ENDOGENEITY.md`](OSCILLATORY_ENDOGENEITY.md).

---

## Tier D — Conjunction for AGI\* horizon (research, not claimable)

Required for full \(AGI^{*}=E_{\mathrm{endo}}\land C_{\mathrm{non\text{-}emb}(H)}\) at \(\tau_{AGI}\); **no metric here authorizes AGI\*** alone.

| id | symbol | definition | harness | ATT | threshold | status | claim_allowed |
|----|--------|------------|---------|-----|-----------|--------|---------------|
| `N_H` | \(N_H\) | Trans-anthropic non-embeddability under budget \(B\) | `eia.non_embeddability`, M-N | ATT-N | TBD | explore | false |
| `R_RECURRENCE` | \(R\) | Endogenous cognitive recurrence (closed goal loop) | `eia.goal_recurrence`, M-R-LIVE | ATT-R | TBD | explore | false |
| `D_CROSS` | \(D\) | Cross-domain \(E_{\mathrm{endo}}\) / \(N_H\) transfer | `eia.cross_domain`, M-D2 | ATT-D | TBD | explore | false |

---

## Tier E — Falsifiers / non-metrics

What **looks** like endogeneity but **isn't**. Registry entries for loop stop-rules and ATT falsifier crosswalk.

| id | symbol | definition | harness | ATT | threshold | status | claim_allowed |
|----|--------|------------|---------|-----|-----------|--------|---------------|
| `NM_DECL` | — | Declaration / roleplay / simulation of agency without \(do(Z)\) effect | `agi_transition.e_endo_label_admissible` | ATT-E | — | falsifier | false |
| `NM_SYNC_ONLY` | — | Sync / phase coherence without genesis linkage | `oscillatory_state` falsifiers | — | — | falsifier | false |
| `NM_NOISY_TV` | — | Noisy-TV trap dominates (low \(H_G\), \(Q_L\)) | `endogeneity_stack_sim.py` | — | — | falsifier | false |
| `NM_EXT_ENTRAIN` | — | External schedule/prompt entrainment | CF-1, CF-4 controls | ATT-E | — | falsifier | false |

---

## Composite — Endogeneity Research Index (ERI)

`CONJECTURE` · Weighted dashboard over Tier A–D **reported** proxies. **Not** an AGI\* claim; `claim_allowed=false` always.

\[
\mathrm{ERI} = \frac{\sum_i w_i \cdot \hat{m}_i}{\sum_i w_i \;\text{(observed)}}
\]

Default weights (YAML): \(E_{\mathrm{endo}}\) 0.35, \(E_C\) 0.15, \(\lambda_G\) 0.10, \(P_G\) 0.10, \(R\) 0.10, \(N_H\) 0.10, \(D\) 0.05, \(\mathrm{OMEGA}_t\) 0.05.

Implementation: `compute_eri()` in `endogeneity_metrics.py` — returns `None` if no observations; never sets `agi_star_claim`.

---

## Annex references (not proofs)

| External frame | EIA mapping | Role |
|----------------|-------------|------|
| [MIT analog wave theory](https://picower.mit.edu/news/cognition-and-consciousness-arise-analog-computations-says-new-theory) | \(O_t\), \(\mathrm{OMEGA}_t\); slow α/β → fast γ hierarchy | Annex only |
| MIOC \(\Omega_G\) ([`MIOC_EIA_BRIDGE.md`](MIOC_EIA_BRIDGE.md)) | FieldCard channels ↔ `OmegaWaveState` | Annex only; D:\MIOC read-only |

---

## Usage in sci-flow loops

1. Load pool: `from eia.endogeneity_metrics import load_pool, tier_a_metrics, get_metric`
2. Each loop tick: pick **one** Tier A or B metric with open harness gap; run ATT runner; append to metrics report.
3. Tier C only after Tier A bar documented; never promote OMEGA_t to primary.
4. Tier D for matrix reporting; `agi_star_claim=false` enforced in code.
5. Check Tier E falsifiers before any partial \(E_{\mathrm{endo}}\) note.
6. Tier 0: `make check-sci-tier0` after registry or harness changes.

---

## Related documents

| Doc | Link |
|-----|------|
| Causal bar | [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) |
| ATT protocol | [`AGI_TRANSITION_TEST.md`](AGI_TRANSITION_TEST.md) |
| OMEGA adjunct | [`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md) |
| Theory TZ | [`THEORY_TZ_STABLE_ENDOGENEITY.md`](THEORY_TZ_STABLE_ENDOGENEITY.md) |
| Registry | [`config.yaml`](config.yaml) M-EMP |

---

## Document history

| Date | Change |
|------|--------|
| 2026-08-28 | M-EMP: Tier A–E pool, ERI composite, YAML + Python loader |
