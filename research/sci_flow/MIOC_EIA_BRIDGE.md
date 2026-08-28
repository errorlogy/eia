# MIOC ↔ EIA Sci-Flow Bridge

**Status:** `OPERATIONAL` crosswalk (read-only external reference)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** **C2**. **No AGI* claim.** MIOC stays **external** — do not copy into repo.

---

## External paths (read-only)

| Resource | Path |
|----------|------|
| Agent README | `D:\MIOC\Recursive_Latent_Field_MAS\recursive_latent_field_arxiv_bundle_v1\README_FOR_AGENTS.md` |
| FieldCard schema | `D:\MIOC\Recursive_Latent_Field_MAS\recursive_latent_field_arxiv_bundle_v1\schemas\fieldcard.schema.json` |
| ND FieldCard schema | `D:\MIOC\...\schemas\nd_fieldcard.schema.json` |
| v44 ablation summary | `D:\MIOC\...\data_summaries\v44_calibrated_policy_summary.csv` |
| Preprint (TeX) | `D:\MIOC\...\Recursive_Latent_Field_MAS_arxiv_preprint_v1.0.tex` |

**Discipline (MIOC):** Do not treat Lambda/Omega/U as physical fields. EIA inherits this: OMEGA_t and O_t are **operational** projections.

---

## 1. Construct crosswalk

| MIOC | EIA sci-flow | Notes |
|------|--------------|-------|
| Group state \(G_k\) | \(S_t^{\mathrm{op}} = (z_t, W_t, M_t, d_t, G_t, O_t)\) | Single-agent operational state |
| Structural field \(\Lambda_G\) | \(W_t, M_t\), belief coverage | COV/FORM/MEM proxies |
| Dynamic field \(\Omega_G\) | O_t + **OMEGA_t** scalar | See [`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md) |
| Control \(U\) | Governor + do(Z)/do(O) interventions | No direct model→action |
| FieldCard_k | ATT trace slice + drive snapshot | Serialize per tick |
| Deficit \(D_k\) | Epistemic gap, prospective tension | CF-4 targets |
| QAT / LCR / FSS | ATT-E / ATT-G / ATT-R rates | Different harnesses; analogous evidence tiers |

---

## 2. omega_state ↔ O_t / OMEGA_t

MIOC `fieldcard.schema.json` `omega_state` properties map to EIA channels:

| FieldCard `omega_state` key | Type | EIA target | Harness |
|-----------------------------|------|------------|---------|
| `phase` | string | Band phase labels; AttREvent tick index | `OmegaWaveState.bands[].phase` |
| `productive_tension` | number | Mid-band amp × slow sync | `psi_oscillatory` feature |
| `collapse_risk` | number | Low OMEGA + high drift | metastability falsifier (future) |
| `decoupling_risk` | number | ATT-R open-loop / no_W arm | `ShadowArm.NO_WORLD_UPDATE` |
| `handoff_continuity` | number | Cross-tick parent chain in AttREvent | ATT-R closed_loop |

MIOC vector definition (preprint §2):

\[
\Omega_G = [\mathrm{phase}, \mathrm{cadence}, \mathrm{synchrony}, \mathrm{productive\ tension}, \mathrm{handoff}, \mathrm{drift}, \mathrm{closure\ velocity}]
\]

EIA `OmegaWaveState` exposes the same channels as bounded floats derived from WoE carriers {20,30,42,70} Hz.

---

## 3. AttREvent ↔ FieldCard step

EIA ATT-R shadow harness (`src/eia/runtime/shadow_multitick.py`):

```python
@dataclass(frozen=True, slots=True)
class AttREvent:
    node_id: str
    kind: str       # W, M, G, Pi, A, X, kuramoto_R, schedule, ...
    label: str
    parent_ids: tuple[str, ...]
    tick: int
    novel: bool
```

| AttREvent.kind | MIOC FieldCard field | Role |
|----------------|----------------------|------|
| `W`, `W_prime` | lambda_state.coverage proxy | World model update |
| `M` | lambda_state.memory_stability | Self-model |
| `G` | omega_state.phase + metrics | Goal genesis |
| `Pi`, `A` | metrics / control_action | Action closure |
| `X`, `schedule` | external entrainment | F-OMEGA-EXT probe |
| `kuramoto_R` | omega_state.synchrony (descriptive) | **Not** E_endo |

FieldCard `step` ↔ AttREvent `tick`. FieldCard `task_id` ↔ shadow episode arm id.

---

## 4. Drive field d_t ↔ lambda/omega deficits

From [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md):

\[
d_{t+1} = \Pi_D\big[(I-\Lambda)d_t + \alpha\Phi_t - B F(g_t) + \xi_t\big], \quad \Phi_t \leftarrow \Phi_t^{\mathrm{base}} + \Psi(O_t)
\]

| MIOC deficit dimension | EIA drive feature | CF-4 / WoE hook |
|------------------------|-------------------|-----------------|
| d_formalism | epistemic_gap | zero_epistemic_gap |
| d_synthesis | prospective_tension | internal_reset |
| d_token | bounded context | ATT-N encoding budget B |
| unresolved_deficits[] | catalog pressure | WoE intent gate |

---

## 5. v44 ablation evidence (no_omega_control)

From `v44_calibrated_policy_summary.csv` (MIOC external):

| Policy | mean_success | Notes |
|--------|--------------|-------|
| controlled_recursive_deficit_6 | 0.807 | Omega control on |
| no_omega_control | 0.802 | Omega control off (−0.5 pp) |
| shuffled_omega | 0.742 | Negative control |

**Interpretation for EIA:** Dynamic field control is **operationally useful** but not dominant; supports treating OMEGA_t as **supporting** order parameter, not primary \(E_{\mathrm{endo}}\). Aligns with M-D (Kuramoto not necessary for WoE intent).

---

## 6. NAMM / T_NAMM correlation

| NAMM id | MIOC hook | EIA milestone |
|---------|-----------|---------------|
| NAMM-2026-013 | kuramoto_R_correlation | M-D (done; not E cause) |
| NAMM-2026-014 | hz_carrier_factorial | M-O / WoE factorial |
| T_NAMM (`L_NAMM_013_030`) | optional soft witness | ATT-N only; not strong \(N_H\) |

NAMM-013 Kuramoto correlation is **descriptive** — same ban as F-KURAMOTO-AS-E. Use for external witness only under T_NAMM topology ([`config.yaml`](config.yaml)).

---

## 7. Import policy

- **Do:** cite paths, schemas, summary CSVs, preprint claims as external reference.
- **Do not:** copy MIOC bundle into `C:\Users\Public\PROACTIVE_AI`.
- **Do not:** claim MIOC QAT/LCR results as EIA C-level evidence without dedicated cross-harness.

---

## Document history

| Date | Change |
|------|--------|
| 2026-08-28 | Initial MIOC↔EIA crosswalk; FieldCard/AttREvent; v44 no_omega_control; NAMM note |
