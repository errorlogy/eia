# Neuroplasticity Vendors ↔ EIA Application Map

**Status:** `CONJECTURE` / **explore adjunct Tier C** (2026-09-01)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim ceiling:** **C2** scoped partial only. **`claim_allowed=false`** for vendor-derived metrics. **No AGI* claim.**  
**Vendors:** [`research/vendor/neuraxon`](../../vendor/neuraxon) · [`research/vendor/graphitti`](../../vendor/graphitti)

---

## Резюме (RU)

**Neuraxon** и **Graphitti** клонированы в `research/vendor/` как внешние модели структурной пластичности и эндогенной активности — **не** в runtime `src/eia/`. Neuraxon: мультитаймскейл синапсы (w_fast/w_slow/w_meta), структурная пластичность, рекуррентные петли, осцилляторный банк + PAC — гипотетический субстрат для **O_t / OMEGA_t** (Tier C). Graphitti: фаза роста (ConnGrowth) + STDP + starter-нейроны без внешнего входа — гипотетический **shadow** для \(W \to M \to d \to G \to A\) при \(X^{\mathrm{trigger}}=0\). Интеграция только через **do(O)**, shadow arms, smoke — без merge в production. Фальсификаторы: Kuramoto R ≠ \(E_{\mathrm{endo}}\); рост структуры ≠ causal bar без ATT-E. Ячейка куба: **D2×L2** ([`SCI_FLOW_3D_CUBE.md`](SCI_FLOW_3D_CUBE.md)). Smoke: `python research/sci_flow/smoke_vendor_neuroplasticity.py`.

---

## Epistemic discipline

| Tag | Meaning |
|-----|---------|
| `CONJECTURE` | Integration hypotheses; falsifiable |
| `OPERATIONAL` | Smoke harness exists |
| `HARD BAN` | Vendor dynamics alone do not establish \(E_{\mathrm{endo}}\) or AGI* |

**Primary bar:** [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) — \(do(Z)\) under non-triggering \(X\).  
**Tier C pool:** [`ENDOGENEITY_METRICS_POOL.md`](ENDOGENEITY_METRICS_POOL.md) — OMEGA_t, \(O_t\), Kuramoto R are explore adjunct only.

---

## 1. What Neuraxon offers

Source: [Neuraxon v2.0](https://github.com/DavidVivancos/Neuraxon) (`neuraxon2.py`, commit `21eff5c` in vendor snapshot).

| Mechanism | Description | EIA relevance |
|-----------|-------------|---------------|
| **Structural plasticity** | Synapse formation/collapse; hidden neuron death; Watts–Strogatz topology | Dynamic **W_t** graph — not static latent |
| **Multi-timescale weights** | `w_fast`, `w_slow`, `w_meta` + AGMP (eligibility × modulator × astrocyte) | \(\tau_{\mathrm{action}} \ll \tau_{\mathrm{goal}} \ll \tau_{\mathrm{meta}}\) ([`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md)) |
| **Continuous-time trinary state** | +1/0/−1 neurons; streaming inputs | Operational recurrence without discrete train/infer split |
| **Neuromodulators + MSTH** | DA/5-HT/ACh/NA; four homeostatic loops | Bounded **d_t** modulation proxy (not claimable as drive field) |
| **Oscillator bank + PAC** | Cross-frequency coupling drives per neuron | Candidate **O_t** generator for M-O / OMEGA_t |
| **ChronoPlasticity / DSN / CTSN** | Per-step Algorithm 1 pipeline | Learned time-warp → analog to slow-band control of fast bands ([`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md)) |
| **Recurrent loops** | Closed update: neuromod → branches → AGMP → homeostasis → structure | Toy **W→M→d→G→A** contour at synaptic scale |

`CONJECTURE` — Neuraxon is a **computational sandbox** for oscillatory + structural endogeneity, not a biological certificate.

---

## 2. What Graphitti offers

Source: [UWB-Biocomputing/Graphitti](https://github.com/UWB-Biocomputing/Graphitti) (commit `b96e96c` in vendor snapshot).

| Mechanism | Description | EIA relevance |
|-----------|-------------|---------------|
| **Growth phase (ConnGrowth)** | Radius-based edge birth/death; `epsilon`, `beta`, `rho`, `targetRate` | **Structural** change of connectivity while sim runs — topology ≠ fixed ANN |
| **STDP (AllDynamicSTDPSynapses)** | Spike-time-dependent synaptic weight updates | Memory/consolidation leg of multi-loop stack |
| **Endogenously active neurons** | Starter neurons: low `Vthresh` + noise → spontaneous firing | \(X^{\mathrm{trigger}}=0\) activity without external drive ([configuration.md](../../vendor/graphitti/docs/User/configuration.md)) |
| **Graph architecture changes** | Edge create/destroy at scale (CPU/GPU) | Long-horizon **ATT-R** recurrence witness at scale (future) |
| **Flexible recorders** | HDF5/XML growth + rate history | External trace comparable to ATT FieldCard slices ([`MIOC_EIA_BRIDGE.md`](MIOC_EIA_BRIDGE.md)) |

`CONJECTURE` — Graphitti models **growth + plasticity + spontaneous activity** as a graph dynamical system; mapping to EIA state vector is **crosswalk**, not identity.

---

## 3. Mapping to EIA concepts

### 3.1 Multi-loop stack (W→M→d→G→A)

From [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md):

\[
W_t \to M_t \to d_t \to G_t \to \Pi_t \to A_t \to \text{Memory/Update} \to d_{t+1}, W_{t+1}, M_{t+1}
\]

| EIA stage | Neuraxon proxy | Graphitti proxy |
|-----------|----------------|-----------------|
| \(W_t\) | Synapse graph + trinary state field | Vertex positions, radii, edge topology |
| \(M_t\) | MSTH gains, neuromod levels, firing-rate averages | Population rate history, neuron type state |
| \(d_t\) | Modulator-driven branch inputs + oscillator drive | Spontaneous starter activity + STDP traces |
| \(G_t\) | Pattern store/recall (`NeuraxonApplication`) | Emergent firing motifs under growth (no explicit goal symbol) |
| \(\Pi_t, A_t\) | Output neuron readout | Spike emission / message passing |
| Memory update | AGMP + structural plasticity | STDP + ConnGrowth |

**Gap (explicit):** Neither vendor exposes EIA **goal genesis gate** \(B_t\) or catalog \(\Delta G\). Vendor runs are **substrate probes**, not ATT-G replacements.

### 3.2 OMEGA_t (Tier C)

[`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md) defines OMEGA_t as bounded scalar from multi-band \(O_t\). Neuraxon’s oscillator bank + PAC is a **hypothesis generator** for band phases/amplitudes feeding `omega_metric()` — **explore adjunct**, `claim_allowed=false`.

Required linkage (F-OMEGA-DECOR): high OMEGA without genesis delta ⇒ decorative.

### 3.3 M-O oscillatory substrate

[`OSCILLATORY_ENDOGENEITY.md`](OSCILLATORY_ENDOGENEITY.md) extends \(S_t^{\mathrm{op}} = (z_t, W_t, M_t, d_t, G_t, O_t)\). Neuraxon oscillators → candidate \(O_t\); Graphitti population rhythms → coarse \(O_t\) summary (rate vectors), not phase-resolved OMEGA without extra instrumentation.

### 3.4 MIOC crosswalk

[`MIOC_EIA_BRIDGE.md`](MIOC_EIA_BRIDGE.md) maps \(\Omega_G\) channels to EIA. Vendor traces could populate **read-only** FieldCard-like slices in shadow harnesses (phase, productive_tension, handoff) — external reference only.

### 3.5 Sci-flow 3D cube — D2×L2

[`SCI_FLOW_3D_CUBE.md`](SCI_FLOW_3D_CUBE.md): **D2 Dynamic × L2 Dynamics** — ATT-R/M-R-LIVE, DSR smoke, OMEGA. This vendor map sits in the same cell as M-O/OMEGA: **Tier C explore**, dynamics harnesses without elevating to Tier A.

---

## 4. Concrete integration hypotheses (research only)

All hypotheses: **shadow / do(O)** arms; **no** production merge into `main/src/eia/`.

| ID | Hypothesis | Harness sketch | Falsifier |
|----|------------|----------------|-----------|
| **H-NX-O** | Neuraxon PAC amplitude correlates with bounded OMEGA proxy when fed into `OmegaWaveState` | Export oscillator phases per step → `omega_metric()` | F-OMEGA-DECOR: high OMEGA, zero \(\Delta G\) |
| **H-NX-STRUCT** | Structural plasticity events predict ATT-R open-loop divergence vs `NO_WORLD_UPDATE` | Count synapse birth/death vs shadow multitick | Structure change without recurrence witness |
| **H-GF-GROWTH** | ConnGrowth edge births sustain activity with zero external Iinject | `test-tiny.xml` + starter neurons; record rate | Activity requires external trigger (violates endogenous premise) |
| **H-GF-STDP** | STDP weight drift under spontaneous activity mimics memory leg of loop | STDP recorder + long run | Weights drift without closed-loop recurrence in EIA shadow |
| **H-CROSS-W** | Vendor \(W\) graph statistics map to EIA `W_prime` events in ATT-R | Compare edge-count/radius vs AttREvent `W` kind | Decorrelation under do(W) |

**Tier assignment:** adjunct **Tier C** in [`ENDOGENEITY_METRICS_POOL.md`](ENDOGENEITY_METRICS_POOL.md); register any new scalar in `endogeneity_metrics.yaml` with `claim_allowed: false`.

---

## 5. Falsifiers

| ID | Statement |
|----|-----------|
| **F-KURAMOTO≠E** | Kuramoto \(R\) or vendor sync alone does **not** imply \(E_{\mathrm{endo}}\) ([`OSCILLATORY_ENDOGENEITY.md`](OSCILLATORY_ENDOGENEITY.md) M-D ban) |
| **F-STRUCT≠E** | Structural growth (ConnGrowth radii, Neuraxon synapse birth) without \(do(Z)\) causal bar does **not** imply endogenous **goal** genesis |
| **F-OMEGA-DECOR** | High OMEGA_t without genesis delta ([`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md)) |
| **F-OMEGA-EXT** | External entrainment mimicking vendor oscillation without internal drive |
| **F-SYNC** | Sync without \(\Delta G\) / ATT-G linkage |

---

## 6. Smoke test

```powershell
python research/sci_flow/smoke_vendor_neuroplasticity.py
```

| Check | Status |
|-------|--------|
| Neuraxon import + 10 `simulate_step()` | **PASS** (pure Python, no pip deps) |
| Graphitti tree + `ConnGrowth` in `test-tiny.xml` | **PASS** (structural) |
| Graphitti binary run | **DEFERRED** — `cmake` not on host; see [`vendor/README.md`](../../vendor/README.md) |

---

## 7. Related documents

| Document | Link |
|----------|------|
| OMEGA wave metric | [`OMEGA_WAVE_METRIC.md`](OMEGA_WAVE_METRIC.md) |
| MIOC bridge | [`MIOC_EIA_BRIDGE.md`](MIOC_EIA_BRIDGE.md) |
| 3D evidence cube D2×L2 | [`SCI_FLOW_3D_CUBE.md`](SCI_FLOW_3D_CUBE.md) |
| Stable endogeneity loops | [`STABLE_ENDOGENEITY.md`](STABLE_ENDOGENEITY.md) |
| Causal bar | [`CAUSAL_ENDOGENEITY.md`](CAUSAL_ENDOGENEITY.md) |
| Vendor install | [`research/vendor/README.md`](../../vendor/README.md) |

---

## 8. Next ticks (sci-loop)

1. Register `VENDOR_NX_PAC` / `VENDOR_GF_RATE` in `endogeneity_metrics.yaml` (Tier C, `claim_allowed: false`).
2. Shadow arm: export Neuraxon oscillator summary → `OmegaWaveState` for one multitick run.
3. CI-friendly Graphitti build (Linux + cmake) in optional workflow — not tier-0 gate.
4. Pre-register do(O) scramble comparing vendor-driven vs harness-native O_t.
