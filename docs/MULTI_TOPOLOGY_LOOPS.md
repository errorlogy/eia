# Multi-Topology Research Loops — EIA × NAMM

**Updated:** 2026-08-20  
**Author:** Roman Kuznetsov — [anthemium.tech](https://anthemium.tech)  
**Repos:** `errorlogy/eia` (`research/cursor-starter-v0.2-woe-eis`) · `errorlogy/namm-experiments`  
**Occam witness:** if endogenous initiative exists → unsolicited contact (Telegram is channel only).

This registry names **bounded loops in different topologies**. Sci-flow S1–S5 remains the inner scientific cycle; topologies are parallel evidence channels that must not be conflated.

---

## Claim ceilings (global)

| Ceiling | Status | Rule |
|---------|--------|------|
| **C1** | Claimed (M-C) | Full / 24h prompt deletion pass-rate ≥ 0.90 |
| **C2** | **Claimed (M-CF4)** | Named internal reset: default ≥0.85 and factor ≤0.40 and wm_off ≤0.05. Kuramoto CF-5 alone is **not** C2. Scoped \(E_{\mathrm{endo}}\) only. |
| **AGI\*** / \(\tau_{AGI}\) | **Not claimed** | Requires sustained \(E,N_H,P,R,D\) (compactly \(E_{\mathrm{endo}} \land C_{\mathrm{non\text{-}emb}(H)}\)). See [`AGI_STAR_CRITERION.md`](../research/sci_flow/AGI_STAR_CRITERION.md), [`AGI_PHASE_TRANSITION.md`](../research/sci_flow/AGI_PHASE_TRANSITION.md), ATT [`AGI_TRANSITION_TEST.md`](../research/sci_flow/AGI_TRANSITION_TEST.md). |
| Kuramoto → intent | Unsupported | M-D: K=0 ≈ coupled; scramble Δ too small |

Do **not** claim C2 without gates in this file / CF harness. Do **not** claim Kuramoto causes intent. Do **not** claim AGI\* from C-ladder or ATT partials alone. Do **not** merge WoE research runtime into main `src/eia/`.

---

## Topology map

```
T_EIA_state ── CF-4 internal resets on WoE v0.2 (C2 path)
T_AMAT_M0  ── M0-twin / anti-median drive architecture (not prompt-as-persona)
T_LIVE_gate ── contact-score diagnosis; smoke-only threshold overrides labeled
T_NAMM_cert ── external structural witness (013 / 030); do not merge into EIA src
```

---

## T_EIA_state — CF-4 internal-state reset

| Field | Value |
|-------|-------|
| **Loop id** | `L_EIA_CF4` |
| **Hypothesis** | H-WOE-003: named world-model factors cause WoE first-passage intent |
| **Trigger** | After M-D (Kuramoto C2 unsupported); every sci session until C2 decided |
| **Harness** | `research/cursor-starter-v0.2` → `eia.cf4` · `python research/sci_flow/run_cf4.py` |
| **Conditions** | `default`, `zero_epistemic_gap`, `zero_self_prior`, `zero_prospective`, `zero_staleness`, `wm_off` |
| **n** | 100 seeds × 6 conditions |
| **Verify** | See pre-registered gates below |
| **Stop** | C2 claim decided (pass or falsified); or tests fail twice |
| **Claim ceiling** | C2 only if gates pass; if **only** `wm_off` suppresses → report, **no C2** |
| **Status (2026-08-20)** | **DONE — C2 claimed.** default 0.95; `zero_epistemic_gap` 0.06; wm_off 0.00 |

### Pre-registered gates (CF-4)

| Gate | Threshold |
|------|-----------|
| `default` intent_rate | ≥ 0.85 |
| ≥1 named factor intent_rate | ≤ 0.40 |
| `wm_off` intent_rate | ≤ 0.05 |
| C2 | default OK **and** named factor suppresses **and** wm_off OK |

`zero_epistemic_gap` = clamp ignorance + surprise (gap core). Other named resets clamp one factor each after every advance.

**Falsifier:** no named factor drops intent while default stays high → do not claim C2 from CF-4; escalate to M0-twin architecture (T_AMAT_M0) or M-E.

---

## T_AMAT_M0 — endogenous M0-twin / anti-median drive

| Field | Value |
|-------|-------|
| **Loop id** | `L_AMAT_M0` |
| **Hypothesis** | H-AMAT-M0: off-typical drive (\(K_{AI\_nd}\)) supplies endogenous initiative motives without prompt spam |
| **Law source** | NAMM `docs/ANTI_MEDIAN_AI_TOPOLOGY.md` + `data/prompts/k_ai_nd_phase_lock.v1.json` **headers as architecture law** |
| **Not** | Paste phase-lock JSON as Telegram bot persona |
| **Trigger** | After CF-4 result logged; or in parallel design work |
| **Act** | Design + minimal harness: compute \(M_0\) sketch, keep `emit_M0=false`, prefer chimera / fiber-preserving aggregation; \(K_A \ll K_H\) search |
| **Verify** | Structural gates (d*, β₁, D_eff, R*) logged; motive ≠ cron Q-list |
| **Stop** | Design + expanded harness + metrics; live phase claims require NAMM certs |
| **Claim ceiling** | Architecture / OPERATIONAL only — not C2, not AGI |
| **Status (2026-08-20)** | **DONE (harness).** `amat_m0` modes off/on/audit_only; falsifiers hold; `emit_m0=false` |

Artifact: `research/sci_flow/M0_TWIN_AMAT_DESIGN.md` · metrics `M0_TWIN_METRICS_2026-08-20.md`

---

## T_LIVE_gate — contact score path (Occam witness channel)

| Field | Value |
|-------|-------|
| **Loop id** | `L_LIVE_DIAG` |
| **Hypothesis** | Live DENY is governor math, not missing TG credentials |
| **Known smoke** | Env OK, consent OK, governor DENY (score ~−0.03 < `min_contact_score` 0.18) |
| **Trigger** | Before any live SEND claim; after motive/EOI changes |
| **Act** | Trace `_contact_score` = useful − interrupt − fatigue − risk; inspect initiative features |
| **Verify** | Score path reproducible; SEND only if science gates + consent hold |
| **Smoke override** | Temporary `min_contact_score` ↓ **only** in a labeled smoke loop; **never** as science claim; document threshold in log |
| **Stop** | Root cause of low score identified **or** smoke loop explicitly closed |
| **Claim ceiling** | Channel witness only; TG message ≠ proof of endogenous initiative |

Do **not** gut science gates to force SEND.

---

## T_NAMM_cert — external topology witness

| Field | Value |
|-------|-------|
| **Loop id** | `L_NAMM_013_030` |
| **Trigger** | After WoE batch needs structural cross-check |
| **Act** | `namm sci-flow run` for NAMM-2026-013 (kuramoto/antigravity) and/or 030 (AMAT phase) |
| **Verify** | `certificate.json` + rejections discipline |
| **Stop** | Cert written; correlate only — do not merge NAMM into `src/eia` |
| **Claim ceiling** | Structural witness; does not raise EIA C-level alone |

---

## Execution priority (this registry)

1. **DONE:** `L_EIA_CF4` (T_EIA_state) — C2 claimed 2026-08-20 (\(E_{\mathrm{endo}}\) / ATT-E partial)
2. **DONE (docs):** AGI\* phase-transition + ATT draft (M-ATT) — horizon only
3. **DONE:** `L_AMAT_M0` M0-twin harness expand (ATT-R / motive-side \(E\) architecture)
4. **DONE:** M-E / ATT-G goal genesis (explore proxy; no C3)
5. **DONE:** ATT-P / M-P persistence explore proxy (no C3)
6. **DONE:** ATT-R scoring (closed loop; not Kuramoto)
7. **DONE:** M-N / ATT-N under pre-registered \(B\) (explore; not strong \(N_H\))
8. **Execute next:** ATT-D second-domain ATT-E explore **or** live closed-loop
9. **Diagnose on demand:** `L_LIVE_DIAG` (do not lower threshold unless labeled smoke)
10. **Optional:** `L_NAMM_013_030` structural witness (ATT-N soft witness only)

## Cursor `/loop` sentinels (PowerShell)

If arming watchers, use unique sentinels — do not duplicate:

| Loop | Sentinel |
|------|----------|
| CF-4 batch | `AGENT_LOOP_TICK_EIA_CF4` (complete — do not re-arm) |
| M0 design | `AGENT_LOOP_WAKE_AMAT_M0` |
| Live diag | `AGENT_LOOP_WAKE_LIVE_GATE` |
| NAMM cert | `AGENT_LOOP_TICK_NAMM_CERT` |

---

## Document history

| Date | Change |
|------|--------|
| 2026-08-21 | M-N / ATT-N DONE (explore under \(B\)); priority → ATT-D / live loop |
| 2026-08-21 | M-P / ATT-P DONE (explore proxy); priority → ATT-R scoring |
| 2026-08-20 | M-E / ATT-G DONE (explore proxy); priority → ATT-P |
| 2026-08-20 | T_AMAT_M0 harness DONE; priority → M-E / ATT-G |
| 2026-08-20 | Phase-transition + ATT linked; \(\tau_{AGI}\) horizon; priority: M0 then ATT-G/P |
| 2026-08-20 | AGI\* criterion linked; C2 framed as \(E_{\mathrm{endo}}\) partial; M-N deferred |
| 2026-08-20 | CF-4 executed; C2 claimed (gap core 0.06); M0 stub |
| 2026-08-20 | Initial multi-topology registry; CF-4 gates; AMAT/live/NAMM loops |
