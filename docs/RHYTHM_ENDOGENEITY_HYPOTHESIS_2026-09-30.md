# Rhythm endogeneity hypothesis (essay import) — 2026-09-30

**Claim ceiling:** C2 · **`claim_allowed=false`** · **no AGI\*** · **`e_endo_support=none`**

This note imports an external essay (Claude, 2026-09-30) into the EIA / sci-flow vocabulary. It is **not** ontology endorsement and does **not** raise the evidence ladder.

---

## 1. Principles (operational reading)

| Principle | Operational meaning in this repo |
|-----------|----------------------------------|
| Rhythms gate **when**, not **who/why** | Timing and gain modulation only; goals and attribution still require D1-style endogeneity criteria (persistence at `X_trigger=0`, influence on other subsystems). |
| Endogeneity needs **content**, not Hz alone | Cross-frequency **phase** coupling, replay, and alpha-style gating are hypothesized *necessary* adjuncts before calling a rhythm “endogenous initiative.” |
| **σ = 0** baseline | With no external drive, any rich timing must come from internal coupling topology—not from labeled “endogenous” periodicity. |
| **Incommensurable ratios** (e.g. φ, e/π) | Quasiperiodic coverage of state space at σ=0; contrasts with a single-frequency **metronome** (strict periodicity, low symbolic diversity). |
| **WoE / carriers** | `OmegaWaveState` and carrier sweeps (20/30/42/70 Hz) test whether a scalar rhythm proxy tracks initiative—not whether biology “is” 42 Hz. |

---

## 2. Mapping to Kairologos battery (Tier C)

| Essay construct | K-* harness | Role |
|-----------------|-------------|------|
| Kuramoto / collective phase | [K-KUR-01](../research/brain_ai/harnesses/k_kur_01_kuramoto_omega_genesis.py), [K-KUR-02](../research/brain_ai/harnesses/k_kur_02_scramble_decorrelation.py) | R vs `OMEGA_t` vs genesis_Δ; F-KURAMOTO-AS-E, F-OMEGA-DECOR |
| Carrier / gamma narrative | [K-WOE-42](../research/brain_ai/harnesses/k_woe_42_carrier_surrogate.py), [K-WOE-42b](../research/brain_ai/harnesses/k_woe_42b_midband_ablation.py) | F-GAMMA-UNIQUE (42 Hz not special at Tier C) |
| Incommensurable vs metronome | [K-RHYTHM-01](../research/brain_ai/harnesses/k_rhythm_01_incommensurable_vs_metronome.py) | σ=0 coupled irrational ratios vs locked metronome; periodicity + sequence novelty |
| Agent binding (content code) | [K-HDC-01/02](../research/agent_eia/harnesses/) | Memory adjunct—not rhythm endogeneity |

Index: [research/kairologos_experiments/README.md](../research/kairologos_experiments/README.md).

**Run (K-RHYTHM-01):**

```powershell
cd C:\Users\Public\PROACTIVE_AI
python research/brain_ai/run_k_rhythm_01.py
pytest tests/test_k_rhythm_01_incommensurable_vs_metronome.py -q
```

Artifact: `research/kairologos_experiments/artifacts/M-K-RHYTHM-01_2026-09-30.json` (`claim_allowed=false`).

---

## 3. Mapping to `endogeneity_topology` findings (A36, A38, B18)

**Repo state at `main` ~`b771ceb`:** `research/endogeneity_topology/FINDINGS.md` is **referenced** in [REPO_AUDIT_2026-09-30.md](./REPO_AUDIT_2026-09-30.md) but **not present on `main`**. The audit summary still anchors:

| ID | Audit paraphrase | Link to rhythm hypothesis |
|----|------------------|---------------------------|
| **A36** | Rhythms set **when**, not **who/why** | Aligns with F-RHYTHM-AS-E annotation in K-RHYTHM-01: high periodicity ≠ E_endo. |
| **A38** | Hierarchy trades combinatorial novelty for localization; thin workspace restores novelty tempo | Motivates **sequence novelty** metric alongside periodicity in K-RHYTHM-01 (symbol diversity, not block Hz). |
| **A38–A39** | Coalition-level novelty under dynamic routing (open thread) | Future: replay + routing ticks in `endogeneity_topology` toy layer—not in K-RHYTHM-01 v0. |
| **B18** | Not spelled out in audit text; **B1–B19** = HCP connectome / metastable boundaries strand | Rhythms essay maps to **gate timescale** probes (`human_connectome/tick77_gate_timescale.py`, `tick76_timescale_brain.py`) as **adjunct** only—no claim that empirical gates imply initiative. |

When `FINDINGS.md` lands on `main`, replace this subsection with direct citations to A36/A38/B18 paragraphs.

---

## 4. Falsification criteria (Tier C)

| Falsifier | If true, then… |
|-----------|----------------|
| **F-RHYTHM-AS-E** | High periodicity + low n-gram novelty treated as endogeneity witness → **reject** rhythm-as-E shortcut (annotation in K-RHYTHM-01). |
| **F-METRONOME-NOVELTY-PARITY** | Metronome matches incommensurable **sequence novelty** at σ=0 → **reject** “irrational ratios required for internal symbol diversity” in this minimal model. |
| **F-KURAMOTO-AS-E** | High Kuramoto R without genesis linkage (K-KUR / K-KUR-02). |
| **F-OMEGA-DECOR** | High `OMEGA_t` decorrelated from genesis (K-KUR-01). |
| **F-GAMMA-UNIQUE** | 42 Hz not distinguished from surrogates (K-WOE-42). |

**Hypothesis survives** only as a **research program**: coupled quasiperiodic timing + content coding + replay + gating must jointly beat metronome/threshold controls on **initiative metrics** (D1), not on rhythm proxies alone.

---

## 5. Repo gap table

| Gap | Status | Target |
|-----|--------|--------|
| σ=0 incommensurable vs metronome harness | **K-RHYTHM-01** (minimal) | Extend duration, multi-seed CI, effect sizes |
| Cross-frequency **phase** coding | Partial via `OmegaWaveState` phases | Explicit PAC / phase-bin readout tick |
| **Replay** at σ=0 | A30–A31 world-memory audit (topology branch) | Non-contingent replay control paired with K-RHYTHM |
| **Alpha gate** | `tick77_gate_timescale` (connectome research) | Wire to EIA shadow session, Tier C only |
| FINDINGS.md A36/A38/B18 on `main` | Missing file | Restore from `research/endogeneity-topology` branch or publish excerpt |
| D1 `e_endo_support` from rhythms | **Out of scope** | Forbidden without world-cut + influence tests |

---

## 6. Suggested experiment (essay → repo)

**Contrast:** (A) three weakly coupled oscillators with frequencies `1, φ, e/π` Hz at σ=0 vs (B) three oscillators locked to a **metronome** master at 1 Hz.

**Metrics:** autocorrelation peak (periodicity proxy), unique n-gram rate on quantized phase vectors (sequence novelty).

**Decision:** If (B) matches (A) on novelty, enrich symbolization/replay; if (A) wins on novelty but not on D1 genesis, keep rhythms as **timing adjunct** per A36.

---

## 7. Links

- [Kairologos experiment index](../research/kairologos_experiments/README.md)
- [Repo audit 2026-09-30](./REPO_AUDIT_2026-09-30.md) (A36, A38–A39, B1–B19)
- [SCI-FLOW cell registry](../research/sci_flow/cell_registry.yaml) (Tier C, `claim_allowed=false`)
- EIA modules: `research/brain_ai/adapters/` (`OmegaWaveState`, shadow bridge), `src/eia/` (production governor—not modified by this hypothesis note)

---

*Document tier: C · Generated 2026-09-30 · No C-ladder raise from this page alone.*
