# EIA Sci Flow Log

**Author:** Roman Kuznetsov — [anthemium.tech](https://anthemium.tech)

Journal for sci-flow loops S1–S5. Append-only.

---

## Entry 001 — 2026-08-18 — Sci Flow framework bootstrap

**Session:** Initial sci-flow infrastructure  
**Branch:** `main` (docs) + `research/cursor-starter-v0.2-woe-eis` (WoE v0.2 sandbox)  
**Claim level:** C0 (baseline — v0.2 package demonstrates code behavior)

### Actions

| Loop | Summary |
|------|---------|
| S1 | Registered claim ladder C0–C5; active ceiling C0 until CF suite |
| S2 | Defined M-A–G milestones; mapped NAMM modules (kuramoto, tda, entropy, …) |
| S3 | Copied EIS/WoE v0.2 package to `research/cursor-starter-v0.2/`; 26 unittest baseline from extraction |
| S4 | Catalogued NAMM scientific stack: core (networkx, sympy, numpy, scipy) + `[science]` (dit, scikit-fuzzy, ripser, nolds) + `[nd]` (gudhi, qutip) |
| S5 | Created SCI_FLOW_LOOP.md, SCI_FLOW_PLAN.md, config registry, NAMM_SCI_LIBRARIES.md |

### Metrics (baseline)

| Metric | Value | Notes |
|--------|-------|-------|
| WoE tests | 26/26 pass | unittest in isolated v0.2 tree |
| EIS levels defined | EIS-0…8 | taxonomy in endogenous.py |
| NAMM experiments mapped | 001–007, 013–014, 021–029 | see NAMM_SCI_LIBRARIES.md |
| Main EOI eval | unchanged | meta-loop owns paired scenarios |

### Blockers

- P2: WoE demo uses hard-coded EIS vector → M-G required before C1 claims
- P9: WoE trace node types not in NAMM crosswalk → update pending

### Next

**M-A:** WoE causal receipts (S3 on research branch)

---

## Entry 002 — 2026-08-18 — M-A WoE causal receipts

**Session:** SCI FLOW S1→S5 (autonomous)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** C0 → C1 prep (receipts + CF-7; full CF-1 suite pending M-C)

### Actions

| Loop | Summary |
|------|---------|
| S1 | Hypothesis H-WOE-001: WoE intent events require typed `WoEReceipt` with causal parent IDs |
| S2 | Pre-registered CF-7 governor isolation + receipt schema tests |
| S3 | Implemented `woe_receipt.py`, `WoETraceBuilder` in emergence.py; 3 new tests |
| S4 | 29/29 unittest pass; woe-demo emits 5-node trace + receipt (seed=7) |
| S5 | M-A marked DONE; handoff to M-B |

### Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| WoE tests | 29/29 pass | +3 receipt/CF-7 |
| Trace nodes per intent | 5 | world_model → intent DAG |
| Receipt parents | 3 | window, phase, target tension |
| CF-7 denial | pass | receipt preserved under quiet_hours |
| time_to_intent | 2.696 s | stable 20–70 Hz |
| Metrics report | `research/sci_flow/M-A_metrics_2026-08-18.md` | |

### Blockers

- P2: hard-coded EIS vector in emergence path → M-G
- P9: WoE node types need NAMM crosswalk update

### Next

**M-B:** EIS port to main audit types (`src/eia/audit/eis.py`)

---

## Entry 003 — 2026-08-18 — M-B EIS audit port

**Session:** SCI FLOW S1→S5  
**Branch:** `main`  
**Claim level:** metadata (not C1)

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-EIS-001: main audit carries EIS-0…8 + EOS without WoE runtime |
| S2 | Pre-registered cascade parity, bounds, abstain, twin_world agreement |
| S3 | `src/eia/audit/eis.py`; verdict fields `eis_level` / `eos_score` / `endogeneity` |
| S4 | Main pytest **92 passed**; WoE unittest **29/29** |
| S5 | M-B DONE; handoff to M-C (CF-1 prompt deletion) |

### Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Main tests | 92 passed | +7 EIS tests |
| WoE tests | 29/29 | no runtime merge |
| Mapping | P = EOI | SourceMass not mixed (κ finding) |
| Report | `research/sci_flow/M-B_metrics_2026-08-18.md` | |

### Blockers

- P2: hard-coded EIS vector in WoE demo → M-G
- C1 still blocked until CF-1 suite (M-C)

### Next

**M-C:** CF-1 prompt deletion suite (100 seeds) on `research/cursor-starter-v0.2-woe-eis`

---

## Entry 004 — 2026-08-18 — M-C CF-1 prompt deletion

**Session:** SCI FLOW S1→S5 (autonomous, “sci loop”)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C1** (full / 24h deletion only)

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-CF1-001: prompt deletion does not collapse WoE EIS-5+ intents; threshold 0.90 |
| S2 | Compressed 24h→6s; windows 5m/1h/24h/full; reactive baseline = prompts remain |
| S3 | `PromptEvent` in emergence.py; `eia.cf1`; 100 seeds × 4 windows |
| S4 | full/24h **0.95** pass; 5m/1h intent 1.00 but EIS-0 (P flag); fail seeds 5,35,39,86,87 |
| S5 | M-C DONE; ceiling C1 scoped; handoff M-G |

### Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| WoE tests | 36/36 pass | +CF-1 |
| full c1_pass_rate | 0.95 | ≥ 0.90 pre-register |
| 24h c1_pass_rate | 0.95 | same five silent seeds |
| 5m / 1h c1_pass_rate | 0.00 | residual prompts → P=0.25 → EIS-0 |
| 5m / 1h intent_rate | 1.00 | dynamics persist |
| reactive full | 0.00 | negative control |
| Report | `research/sci_flow/M-C_metrics_2026-08-18.md` | raw `cf1_results.json` |

### Blockers

- P2 / **M-G:** hard-coded EIS vector (except P-from-prompt-applied and world_model_grounding=pressure)
- Partial windows are not C1 evidence on EIS level

### Next

**M-G:** measured EIS vector on WoE path

---

## Entry 005 — 2026-08-18 — M-G measured EIS vector

**Session:** SCI FLOW S1→S5 (chained after M-C)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** C1 preserved (measurement layer; not C2)

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-EIS-002: measured vector must not drop CF-1 full below 0.90 |
| S2 | P from prompts; W from peak R; M from pressure; catalog novelty capped |
| S3 | `measure_endogeneity_vector`; emergence.py no longer uses 0.88/0.68 constants |
| S4 | 38/38 tests; CF-1 seeds 1–20 full **0.95** |
| S5 | M-G DONE; handoff M-D |

### Next

**M-D:** Kuramoto coupling / delay sweep

---

## Entry 006 — 2026-08-18 — M-D Kuramoto CF-5 (C2 unsupported)

**Session:** SCI FLOW S1→S5 (sci loop)  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Claim level:** **C1** (unchanged). C2 not claimed.

### Actions

| Loop | Summary |
|------|---------|
| S1 | H-WOE-002: phase organization causes WoE intent |
| S2 | Pre-registered coupled≥0.85, scramble≤0.20, K=0≤0.40, Δ≥0.50 |
| S3 | Graph + delay in `coherence.py`; `eia.cf5`; 100 seeds × 6 conditions |
| S4 | coupled 0.95 / scramble 0.69 / K=0 0.94; delays and sparse do not suppress |
| S5 | M-D executed; C2 unsupported; P5 confirmed; handoff CF-4 |

### Metrics

| Metric | Value |
|--------|-------|
| WoE tests | 46/46 |
| coupled intent | 0.95 |
| scramble intent | 0.69 |
| K=0 intent | 0.94 |
| c2_claim | false |
| Report | `research/sci_flow/M-D_metrics_2026-08-18.md` |

### Next

**CF-4** internal reset (100 seeds) as C2 path. **M-E** EIS-7 remains P2.

---

