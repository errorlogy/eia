# M-O Neuraxon / Graphitti — Endogeneity Factor Analysis

**Status:** `CONJECTURE` / **explore adjunct Tier C** (2026-09-01)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** **C2** scoped partial only. **`claim_allowed=false`**. **No AGI\*** claim. **No WoE→main merge.**  
**Vendors:** [`research/vendor/neuraxon`](../../vendor/neuraxon) · [`research/vendor/graphitti`](../../vendor/graphitti)  
**Probe:** `python research/sci_flow/run_mo_neuroplasticity_probe.py` → [`M-MO_neuroplasticity_probe_2026-09-01.json`](M-MO_neuroplasticity_probe_2026-09-01.json)

---

## Резюме (RU)

**Тезис:** Neuraxon и Graphitti — **внешние Tier C субстраты** эндогенной динамики для sci-flow M-O, **не** runtime EIA. Neuraxon даёт мультитаймскейл пластичность (w_fast/w_slow/w_meta), структурный рост и осцилляторный банк + PAC → гипотеза **O_t / OMEGA_t**. Graphitti (ConnGrowth + STDP + starter-нейроны) моделирует **рекуррентную активность при X^trigger=0** без внешнего Iinject. Ни один вендор **не** удовлетворяет полный каузальный бар **E_endo** без **do(Z)** на EIA-стеке; частично покрывают P1–P2 (внутренняя динамика, нулевой внешний триггер), но **проваливают P3/P5** (нет do(Z)→ΔG в ATT-G). Размещение в кубе: **D2×L2** (динамика), инварианты **D2×L1**. Фальсификаторы: oscillation≠initiative (F-OMEGA-DECOR), growth≠E_endo (F-STRUCT≠E), Kuramoto≠E (F-KURAMOTO-AS-E). Probe harness: `run_mo_neuroplasticity_probe.py`, tier C, claim_allowed=false.

---

## Epistemic discipline

| Tag | Meaning |
|-----|---------|
| `CONJECTURE` | Vendor→EIA mapping hypotheses; falsifiable |
| `OPERATIONAL` | Probe harness + smoke exist |
| `HARD BAN` | Vendor dynamics alone do **not** establish \(E_{\mathrm{endo}}\) or AGI\* |

**Primary bar:** [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md)  
**Application map:** [`NEUROPLASTICITY_EIA_APPLICATION.md`](NEUROPLASTICITY_EIA_APPLICATION.md)  
**Oscillatory adjunct:** [`OSCILLATORY_ENDOGENEITY.md`](OSCILLATORY_ENDOGENEITY.md) · [`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md)

---

## 1. Position in EIA stack

Neuraxon and Graphitti sit **below** the production EIA cognitive loop — as **research-only computational sandboxes** for endogeneity *substrate* hypotheses, not as merged modules in `main/src/eia/` or `research/cursor-starter-v0.2/src/eia/runtime/`.

```
                    ┌─────────────────────────────────────┐
  External X_t  ──► │  Observation / Twin / EOI-k         │
                    │  Governor · AuthenticReason           │
                    └──────────────┬──────────────────────┘
                                   │
         ┌─────────────────────────▼─────────────────────────┐
         │  EIA production stack (W→M→d→G→A→Memory)         │
         │  CognitiveLoop · DriveField · Goal genesis B_t    │
         │  OmegaWaveState (native M-O stub)                 │
         └─────────────────────────┬─────────────────────────┘
                                   │ shadow / do(O) crosswalk only
         ┌─────────────────────────▼─────────────────────────┐
         │  Tier C vendor adjunct (NOT runtime merge)        │
         │  ┌──────────────┐    ┌──────────────────────┐     │
         │  │  Neuraxon    │    │  Graphitti           │     │
         │  │  O_t PAC     │    │  ConnGrowth + STDP   │     │
         │  │  w_fast/slow │    │  starter neurons     │     │
         │  └──────────────┘    └──────────────────────┘     │
         └───────────────────────────────────────────────────┘
```

| EIA component | Neuraxon role | Graphitti role | Merge? |
|---------------|---------------|----------------|--------|
| **W_t** (world model) | Dynamic synapse graph, Watts–Strogatz topology | Vertex layout + growing edge set | **No** — crosswalk only |
| **M_t** (self-model) | MSTH gains, neuromod levels | Population rate history (if recorder run) | **No** |
| **d_t** (drive field) | Oscillator PAC → hypothetical \(\Psi(O_t)\) | Spontaneous starter activity | **No** — not five-channel \(d_t\) |
| **G_t** (goal genesis) | Pattern store/recall layer | *None* — no goal symbol | **Gap** |
| **Governor** | *None* | *None* | N/A |
| **Memory** | AGMP + structural plasticity | STDP + ConnGrowth | Shadow witness only |
| **O_t / OMEGA_t** | Primary vendor hypothesis | Coarse rate rhythm (no phase PAC) | Feed `omega_metric()` explore |

**Discipline:** Integration is via **do(O)** interventions registered in `intervention_cube.py`, shadow multitick arms, and probe JSON — never production import of `neuraxon2` or Graphitti binary into the daemon path.

---

## 2. Endogeneity factor analysis

### 2.1 Neuraxon — multi-timescale plasticity → O_t

| Mechanism | Vendor locus | EIA mapping | Endogeneity contribution |
|-----------|--------------|-------------|--------------------------|
| **w_fast / w_slow / w_meta** | `Synapse` AGMP updates | \(\tau_{\mathrm{action}} \ll \tau_{\mathrm{goal}} \ll \tau_{\mathrm{meta}}\) ([`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md)) | Sustained internal state evolution **without** external input when `simulate_step()` runs with empty inputs |
| **Structural plasticity** | `_apply_structural_plasticity()` | Dynamic **W_t** | Topology change under X^trigger=0 — ATT-R *substrate* witness, not ATT-R pass |
| **OscillatorBank + PAC** | `theta` gates `gamma` in `get_drive()` | Candidate **O_t** bands → `OmegaWaveState` | OMEGA_t explore; **F-OMEGA-DECOR** if no \(\Delta G\) |
| **Neuromodulators (DA/5-HT/ACh/NA)** | `NeuromodulatorSystem` | Bounded **d_t** proxy (not claimable) | Modulates plasticity gates; not EIA DriveField |
| **MSTH four loops** | `MSTHState` ultrafast→slow | Metastability \(\mathfrak{E}\) support | Slow structural pressure drives synapse birth |

`CONJECTURE` — Neuraxon is the **richest vendor hypothesis** for M-O because it already implements cross-frequency coupling analogous to slow-control × fast-engagement in `omega_metric()`.

### 2.2 Graphitti — growth + STDP + starter activity

| Mechanism | Vendor locus | EIA mapping | Endogeneity contribution |
|-----------|--------------|-------------|--------------------------|
| **ConnGrowth** | `ConnectionsParams class="ConnGrowth"` | Dynamic **W_t** at scale | Edge birth/death while sim runs — structural endogeneity *factor* |
| **STDP** (`AllDSSynapses` / dynamic variant) | `EdgesParams` | Memory/consolidation leg | Weight drift under spontaneous activity |
| **Starter neurons** | `starter_vthresh` < `Vthresh` + noise | \(X^{\mathrm{trigger}}=0\) firing | **Recurrence without external Iinject** — key falsifier target for F-EXT |
| **HDF5/XML recorders** | `RecorderParams` | FieldCard-like slices ([`MIOC_EIA_BRIDGE.md`](MIOC_EIA_BRIDGE.md)) | External trace for shadow compare |

`CONJECTURE` — Graphitti tests the **“activity without trigger”** leg of stable endogeneity more directly than Neuraxon (which can run with zero external inputs but is not spike-resolved).

### 2.3 Map to \(E_{\mathrm{endo}}\) causal bar (P0–P5)

Using the ATT-E bar from [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) plus proof-protocol gates ([`EIA_PROOF_PROTOCOL.md`](EIA_PROOF_PROTOCOL.md)):

| Gate | Statement | Neuraxon | Graphitti | Without do(Z) on EIA |
|------|-----------|----------|-----------|----------------------|
| **P0** | Trajectory / goal distribution \(\Delta G\) | **Fail** — no goal symbol | **Fail** — spike rates only | **Fail** |
| **P1** | Change attributable to internal dynamics | **Partial** — closed `simulate_step` loop | **Partial** — starter + growth loop | N/A (vendor isolated) |
| **P2** | No matching external initiator (\(X^{\mathrm{trigger}}=0\)) | **Partial** — zero external inputs possible | **Partial** — starter neurons by design | **Partial** at vendor layer |
| **P3** | \(do(Z)\) shifts \(P(G_{t+1})\) | **Fail** — no Z/G in vendor | **Fail** | **Required** — only EIA CF-4 path |
| **P4** | F-DECL / F-NARR / F-EXT absent | **N/A** | **N/A** | Vendor cannot satisfy |
| **P5** | Proof protocol `e_endo_support=partial` admissible | **Fail** — metric not in Tier A pool | **Fail** | **Fail** — Tier C only |

**Summary:** Vendors contribute **D2 dynamic substrate evidence** (oscillation, plasticity, spontaneous activity) — **not** Tier A \(E_{\mathrm{endo}}\). Partial credit on **P1–P2** at the computational-sandbox layer; **P0, P3, P5 fail** until bridged to EIA `do(Z)` / ATT-G harness.

---

## 3. Causal identification — proposed do(O) interventions

Registered in `research/cursor-starter-v0.2/src/eia/intervention_cube.py` (D2×L2):

| ID | Intervention | Intent | Falsifiers |
|----|--------------|--------|------------|
| `do_o_neuraxon_plasticity_off` | Freeze w_fast/w_slow/w_meta + disable structural birth | If OMEGA_t / activity unchanged → oscillation not plasticity-driven | F-OMEGA-DECOR, F-STRUCT≠E |
| `do_o_graphitti_growth_off` | ConnGrowth ε→0 or static `ConnStatic` config swap | If activity persists → not growth-dependent; if vanishes → growth necessary but ≠ E_endo | F-STRUCT≠E, F-EXT |
| `do_o_phase_scramble` (existing) | Kuramoto / band phase scramble | Sync without genesis | F-SYNC, F-KURAMOTO-AS-E |
| `do_o_omega_decor` (existing) | Multi-band OMEGA decorrelation | Decorative OMEGA | F-OMEGA-DECOR |

### Falsifiers (pre-registered)

| ID | Statement | Vendor test |
|----|-----------|-------------|
| **F-KURAMOTO-AS-E** | Kuramoto R or vendor sync ≠ \(E_{\mathrm{endo}}\) | High `kuramoto_r_final` in probe JSON does not raise C-level |
| **F-OMEGA-DECOR** | High OMEGA_t without \(\Delta G\) | Neuraxon `omega_t.final` decorative until ATT-G linked |
| **F-STRUCT≠E** | Structural growth ≠ causal goal genesis | ConnGrowth edge delta ≠ ATT-G pass |
| **F-EXT** | Activity requires external trigger | Graphitti with starter off should collapse (probe future arm) |
| **oscillation≠initiative** | O_t moves but Governor/initiative flat | Shadow multitick with vendor-fed O_t only |

**Pass pattern (explore only):** Under \(X^{\mathrm{trigger}}=0\), do(O) vendor arm changes EIA shadow \(\Delta G\) **and** matched do(Z) controls hold **and** falsifiers do not fire. **No such pass exists today.**

---

## 4. Empirical hooks

### 4.1 Probe harness

```powershell
python research/sci_flow/run_mo_neuroplasticity_probe.py
# optional: python research/sci_flow/run_mo_neuroplasticity_probe.py 100
```

| Arm | Action | Output fields |
|-----|--------|---------------|
| **Neuraxon** | 50× `simulate_step()`, seed=42 | `omega_t`, `kuramoto_r_final`, `plasticity`, `synapse_count`, `oscillator_bands_final` |
| **Graphitti** | Parse `test-tiny.xml`, document build | `conn_growth_params`, `has_starter_neurons`, `stub_metrics` if binary missing |

Artifact: [`M-MO_neuroplasticity_probe_2026-09-01.json`](M-MO_neuroplasticity_probe_2026-09-01.json) — **`claim_allowed=false`**, **tier C**.

### 4.2 Smoke (tier-0 friendly)

```powershell
python research/sci_flow/smoke_vendor_neuroplasticity.py
```

### 4.3 Future arms (not tier-0 gate)

1. Neuraxon oscillator export → `OmegaWaveState.from_carrier_phases` → one shadow multitick.
2. Graphitti CI build (Linux + cmake) → spike-rate recorder → `VENDOR_GF_RATE` in `endogeneity_metrics.yaml`.
3. Paired do(O): `plasticity_off` vs `growth_off` vs native `oscillatory_state.py`.

---

## 5. 3D cube placement

From [`SCI_FLOW_3D_CUBE.md`](SCI_FLOW_3D_CUBE.md):

| Cell | Placement | Content |
|------|-----------|---------|
| **D2×L1** Invariants | **filled** (extended) | F-KURAMOTO-AS-E, F-STRUCT≠E, F-OMEGA-DECOR; vendor hard ban |
| **D2×L2** Dynamics | **partial → filled** (probe) | M-O vendor probe, do(O) registry, Neuraxon/Graphitti harness |
| **D2×L3** Witness | **partial** | `M-MO_neuroplasticity_probe_2026-09-01.json`; Graphitti binary witness deferred |

### Invariants preserved (D2×L1)

| Invariant | Neuraxon preserves | Graphitti preserves |
|-----------|-------------------|---------------------|
| No AGI\* from oscillation alone | ✓ (PAC ≠ goal) | ✓ (spikes ≠ goals) |
| C2 ceiling | ✓ | ✓ |
| Kuramoto ≠ E | ✓ — R is logged, not claimed | N/A (no Kuramoto) |
| X^trigger=0 activity hypothesis | ✓ with empty inputs | ✓ via starter neurons |
| Governor / side-effect ban | ✓ (sandbox) | ✓ (sandbox) |
| WoE→main merge ban | ✓ | ✓ |

---

## 6. Comparison table

| Dimension | **Neuraxon** | **Graphitti** | **EIA `oscillatory_state.py`** | **Kuramoto stub** (M-D / CF-5) |
|-----------|--------------|---------------|-------------------------------|--------------------------------|
| Language | Python | C++/CUDA | Python | Python (WoE sim) |
| **O_t source** | Multi-band PAC oscillator bank | Population rate rhythm (coarse) | `OscillatoryBand` + `OmegaWaveState` | Phase oscillators only |
| **Plasticity** | w_fast/slow/meta + structural | STDP + ConnGrowth | None (state injection) | None |
| **X^trigger=0 activity** | Yes (no external input) | Yes (starter neurons) | Injected / synthetic | Coupled phases only |
| **OMEGA_t** | Via `omega_metric()` on exported bands | Not phase-resolved | Native `omega_metric()` | Uses R — **banned as E** |
| **ATT-G / B_t** | No | No | No (adjunct) | No |
| **Tier** | C | C | C | C (negative control) |
| **claim_allowed** | false | false | false | false |
| **E_endo path** | Substrate → do(O) shadow | Substrate → recurrence witness | M-O native explore | Falsifier only |

---

## 7. arXiv integration (Discussion M-O)

Suggested addition to `arxiv/main.tex` §M-O Tier C Horizon:

> Beyond native Kuramoto and OMEGA$_t$ stubs, we clone **Neuraxon** (multi-timescale synaptic plasticity, PAC oscillator bank) and **Graphitti** (ConnGrowth topology dynamics, STDP, endogenously active starter neurons) as **Tier C computational sandboxes**—adjunct substrates for oscillatory and structural endogeneity hypotheses under `claim_allowed=false`. These vendors occupy the same D2$\times$L2 cell as M-O explore metrics; they do **not** satisfy the ATT-E causal bar without $do(Z)$ evidence on the EIA stack, and high synchrony or structural growth alone are pre-registered falsifiers (F-KURAMOTO-AS-E, F-STRUCT$\neq$E).

---

## 8. Related documents

| Document | Role |
|----------|------|
| [`NEUROPLASTICITY_EIA_APPLICATION.md`](NEUROPLASTICITY_EIA_APPLICATION.md) | Vendor application map |
| [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) | Primary E_endo bar |
| [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md) | W→M→d→G→A loops |
| [`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md) | OMEGA_t definition |
| [`MIOC_EIA_BRIDGE.md`](MIOC_EIA_BRIDGE.md) | Ω_G crosswalk |
| [`SCI_FLOW_3D_CUBE.md`](SCI_FLOW_3D_CUBE.md) | Evidence cube |
| [`research/vendor/README.md`](../../vendor/README.md) | Install / build |

---

## Document history

| Date | Change |
|------|--------|
| 2026-09-01 | M-O Neuraxon/Graphitti endogeneity factor analysis; probe harness; do(O) registry; cube D2×L2 |
