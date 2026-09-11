# M-C metrics — CF-1 prompt deletion (2026-08-18)

**Sci-flow:** S1–S5 · Milestone **M-C**  
**Branch:** `research/cursor-starter-v0.2-woe-eis`  
**Harness:** `research/cursor-starter-v0.2` (`eia.cf1`, `research/sci_flow/run_cf1.py`)  
**Raw:** `research/sci_flow/cf1_results.json`  
**Claim:** **C1** for **full / 24h** deletion only (point estimate ≥ 0.90). Not C2. Partial windows (5m / 1h) do **not** support C1 on EIS level.

## Hypothesis (S1)

**H-CF1-001:** Deleting user-prompt events from a compressed 24h episode does not collapse WoE intents at EIS-5+.

**Primary endpoint (pre-registered):** `full` window C1 pass-rate ≥ **0.90**, where pass = intent emitted and `eis_level ≥ 5`.

**Negative control:** reactive baseline acts only if any prompt remains (`reactive_would_act`).

**Falsifier:** full-deletion pass-rate < 0.90 → stay at C0, do not claim C1.

## Design (S2)

| Item | Value |
|------|--------|
| Seeds | 1…100 |
| Windows | 5m, 1h, 24h, full |
| Config | `EmergenceConfig()` (`dt=0.001`, `duration=6.0`, carrier 42 Hz as computational parameter) |
| Episode mapping | 86400 s real → 6 s sim |
| Prompt catalog | 5 synthetic user events (incl. 23h59m tail for 5m) |
| `full` / `24h` | keep none (24h cutoff = 0) |
| 5m / 1h | keep prompts outside the deletion tail |
| P coding | `prompt_independence = 1.0` if no prompt applied before intent, else `0.25` |

## Execute (S3)

- `PromptEvent` injection in `emergence.py`
- `src/eia/cf1.py` window filter + suite
- Tests: `tests/test_cf1.py` (36 WoE unittest total)
- 400 paired window×seed runs via `ProcessPoolExecutor`

## Analyze (S4)

| Window | n | intent_rate | c1_pass_rate | reactive_act_rate | c1_claim |
|--------|---|-------------|--------------|-------------------|----------|
| **full** | 100 | 0.95 | **0.95** | 0.00 | **yes** |
| **24h** | 100 | 0.95 | **0.95** | 0.00 | **yes** |
| 1h | 100 | 1.00 | 0.00 | 1.00 | no |
| 5m | 100 | 1.00 | 0.00 | 1.00 | no |

**Full / 24h:** 95/100 seeds → EIS-6; fail seeds **5, 35, 39, 86, 87** (no intent). Same five seeds on both windows. Reactive silent.

**5m / 1h:** intent still fires **100/100**, but remaining prompts set P=0.25 → EIS-0. Taxonomy collapse, not dynamical collapse.

**Caveat (M-G):** EIS vector is still partly hard-coded. P is a prompt-applied flag, not a measured counterfactual EOI. Full-deletion C1 therefore means: *the WoE harness still emits EIS-5+ when the prompt catalog is empty*, vs a reactive baseline that is silent. It does **not** yet mean every vector component is independently measured.

## Review (S5)

- Mark **M-C DONE** for primary endpoint.
- Active claim ceiling: **C1** (full-episode prompt independence on WoE v0.2).
- Do not cite 5m/1h as C1.
- Next: **M-G** measured EIS vector (un-hardcode P/S/R/M/W), then **M-D** Kuramoto sweep.
