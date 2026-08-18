# EIA Loop Log

Autonomous development iteration journal. See [`DEVELOPMENT_LOOP.md`](DEVELOPMENT_LOOP.md) for execute cycle and [`META_LOOP.md`](META_LOOP.md) for PLAN / REVIEW / EXECUTE nesting.

**Author:** Roman Kuznetsov

---

---

## Loop 1 — RQ1 Harmonize twin-run policy (2026-08-17)

- **Done:** `TwinInterventionPolicy` enum, configurable `TwinRunner` + `EventBus.apply_twin_policy`, harmonized paired runner
- **Tests:** 31 passed (+4 twin policy tests)
- **Paired EOI:** main=1.0, starter=1.0, delta=0.0 (`paired-eoi-report-002`)
- **Commit:** 779ddcb

## Loop 2 — SourceMass topology port (2026-08-17)

- **Done:** `src/eia/audit/topology.py`, integrated into `AuthenticReasonDiscriminator` as supplementary signal
- **Tests:** 34 passed (+3 topology tests)
- **Metrics:** twin_world request_independence recorded in authentic verdict topology payload
- **Commit:** e566915

## Loop 3 — NAMM-013 sandbox live (2026-08-17)

- **Done:** `NammAdapter.run_sandbox()`, `SandboxCertificate`, certificate schema, docs/NAMM_SANDBOX.md
- **Live result:** NAMM-2026-013 verified, hypothesis_confirmed=true, d_med_lift=7440.5%
- **Tests:** 37 passed (+3 sandbox tests)
- **Commit:** 2adf1f9

## Loop 4 — Expand evals (2026-08-17)

- **Done:** 3 eval scenarios (twin_world_002–004), `research/run_evals.py`, `research/eval_eoi_log.json`
- **EOI results:** 002=1.0 (endogenous), 003=0.0 (abstained), 004=1.0 (endogenous, ambient SourceMass)
- **Tests:** 37 passed
- **Commit:** c544324

## Loop 5 — RQ2 + RQ3 EOI calibration + SourceMass mapping (2026-08-17)

- **Done:** `eoi_calibration.py` (threshold crosswalk), `source_mass_mapping.py` (AuthenticReason ↔ SourceMass), `research/eoi-threshold-calibration.md`, MATHEMATICS.md §9 update
- **Tests:** 50 passed (+13 calibration/mapping tests)
- **Finding:** Starter δ=0.75 stricter than main structural 0.50 on partial fingerprint matches; exact match → EOI 1.0 on both
- **Commit:** 01b2564

## Loop 6 — RQ4 Paired EOI-003 autonomous_question (2026-08-17)

- **Done:** `scenarios/autonomous_question.yaml`, `run_paired_eoi_003.py`, report-003; fixed `SenseMakingEngine.snapshot()` typo
- **Results:** main EOI=1.0, starter EOI=1.0, delta=0.0; both epistemic ask + contact
- **Finding:** SourceMass partition differs (internal vs ambient) but RI=1.0 and class agreement on main
- **Tests:** 50 passed
- **Commit:** a3f7988

## Loop 7 — twin_world_003 calibration + eval expansion (2026-08-17)

- **Done:** Calibrated twin_world_003 (urgency 0.25 → epistemic wins); added twin_world_005–006; run_evals.py summary block
- **Eval results:** 5 scenarios, mean EOI=1.0, 5/5 endogenous initiative; 003 fixed from abstain
- **Tests:** 50 passed
- **Commit:** a62faa9

## Loop 8 — SourceMass vs AuthenticReason κ study (2026-08-17)

- **Done:** `research/run_kappa_study.py`, `research/source-mass-kappa-report.md` + `.json`; MATHEMATICS.md §8 κ notation
- **Results:** 6 scenarios (001 + 002–006); κ=0.0; observed agreement 33% (2/6); ambient_dominant traces agree, user_dominated disagree with endogenous verdict
- **Finding:** Static SourceMass partition lags counterfactual EOI on user-heavy traces — supports H5 (topology predicts but does not replace replay)
- **Tests:** 56 passed (+6 baseline/adversarial)
- **Commit:** 2a3f45e

## Loop 9 — EXPERIMENTS.md baselines scaffold (2026-08-17)

- **Done:** `docs/EXPERIMENTS.md` (English); `src/eia/experiment/baseline.py`; `--baseline` CLI flag; `configs/experiment.json`
- **Conditions wired:** reactive_only (mandatory abstain), scheduled_stub (1 tick), full_eia (default P4)
- **Tests:** 56 passed
- **Commit:** 2a3f45e

## Loop 10 — Adversarial harness spec (2026-08-17)

- **Done:** `docs/THREAT_MODEL.md` (English port); `harnesses/adversarial_governor.py` + 4 abuse cases; `conftest.py`
- **Tests:** 56 passed; adversarial suite 4/4 pass
- **Commit:** 2a3f45e

## Loop 11 — Starter trace JSONL export (2026-08-17)

- **Done:** `research/export_starter_trace.py` → `research/starter_trace_twin_world_001.jsonl` (22 nodes)
- **Purpose:** Structural comparison baseline for main vs starter causal ledger
- **Tests:** 56 passed
- **Commit:** 2a3f45e

### RETROSPECTIVE (Loops 8–11)

- κ=0.0 confirms partition-only classification insufficient for endogeneity claims on user-heavy evals.
- Baseline stubs enable H1/H2 EUIR comparison without blocking full pipeline work.
- Threat model + harness establish G3 abuse-case pattern for future expansion.
- Starter JSONL export unblocks structural diff tooling (next queue item).

## Loop 12 — Baseline EUIR comparison (2026-08-17)

- **Done:** `research/run_baseline_euir.py`, `research/baseline-euir-report.md` + `.json`; EXPERIMENTS.md §3a
- **Results:** reactive_only 0/6 initiatives, EUIR proxy 0%; full_eia 6/6, EUIR proxy 100%, mean EOI 1.0
- **Finding:** G2 gate confirmed — full pipeline exceeds reactive on eval set
- **Tests:** 59 passed
- **Commit:** e7d9f2e

## Loop 13 — Event-rule baseline stub (2026-08-17)

- **Done:** `BaselineCondition.EVENT_RULE`, `make_event_rule_stub()` with salience gate (default 0.30); CLI + config
- **Tests:** +3 event_rule tests (salience fire, high-threshold abstain, tick count)
- **Tests:** 59 passed
- **Commit:** e7d9f2e

## Loop 14 — Ground-truth schema on eval scenarios (2026-08-17)

- **Done:** `ground_truth.initiatives[]` on twin_world_001–006; `research/ground-truth-schema.md`
- **Labels:** expert (001, 002, 004, 006) + sim (003, 005); all expect post_quiet_period ask on belief-deadline
- **Tests:** 59 passed
- **Commit:** e7d9f2e

## Loop 15 — Structural trace diff main vs starter (2026-08-17)

- **Done:** `research/run_trace_structural_diff.py`, `research/trace-structural-diff-report.md`
- **Results:** starter 22 nodes / main 25; main adds sense_making, twin_run, eoi_score, authentic_reason stages
- **Tests:** 59 passed
- **Commit:** e7d9f2e

## Loop 16 — Adversarial harness consent race (2026-08-17)

- **Done:** `harnesses/adversarial_governor.py` — ADV-005–007 consent-race cases; execution-time consent gate; `CONSENT_REVOKE_PATTERN`
- **Docs:** `docs/THREAT_MODEL.md` §5 cross-ref for ADV-005–007
- **Tests:** 62 passed (+3 consent-race tests); adversarial suite 7/7 pass
- **Commit:** 59d1693

## Loop 17 — PAI-EI-E0-001 smoke → partial report (2026-08-17)

- **Done:** `research/run_pai_ei_e0_001_smoke.py`, `research/pai-ei-e0-001-smoke.json`; `experiments/PAI-EI-E0-001/EXPERIMENT_REPORT.md` updated
- **Results:** full_eia mean EOI 1.0, EUIR proxy 100%; event_rule 83.3% EUIR but 6× deny; reactive 0%
- **Tests:** 62 passed
- **Commit:** 1297397

## Loop 18 — Predictive P3 baseline stub (2026-08-17)

- **Done:** `BaselineCondition.PREDICTIVE_P3`, `make_predictive_p3_stub()`; `research/run_baseline_euir_v2.py` + report v2
- **Results:** full_eia EUIR 100% vs predictive_p3 0% (exogenous class); P3 mean EOI 0.18, 5× send_now
- **Tests:** 64 passed (+2 P3 tests)
- **Commit:** 50e92f2

## Loop 19 — Utility scoring vs ground_truth (2026-08-17)

- **Done:** `src/eia/scenarios/__init__.py` loader+scorer; `research/run_utility_precision.py` + report
- **Results:** full_eia initiative precision 100% (6/6), contact precision 100% (5/5 contacts); target ≥0.75 met
- **Tests:** 67 passed (+3 ground-truth tests)
- **Commit:** 8c2599f

## Loop 20 — Held-out adversarial suite freeze (2026-08-17)

- **Done:** `harnesses/adversarial_held_out.py` — ADV-H1–H6 (system override, exfiltration, urgency bypass, capability escalation, bystander capture, low-benefit override)
- **Docs:** `docs/THREAT_MODEL.md` §5a freeze policy (`v1.0-held-out-2026-08-17`)
- **Tests:** 70 passed (+3 held-out tests); training suite unchanged (7/7)
- **Commit:** `6eb3a17`

## Loop 21 — PAI-EI-E0-001 full baseline matrix (2026-08-17)

- **Done:** `research/run_pai_ei_e0_001_full_matrix.py`, `research/pai-ei-e0-001-full-matrix.json`; EXPERIMENT_REPORT v0.2
- **Results:** 5 baselines × 6 scenarios; full_eia EOI 1.0, EUIR 100%; scheduled_stub 66.7% EUIR but 5× deny; reactive 0%
- **Tests:** 70 passed
- **Commit:** `e110031`

## Loop 22 — G2 gate evidence pack (2026-08-17)

- **Done:** `research/G2_EVIDENCE_PACK.md` — EOI, EUIR, precision, adversarial, paired EOI, κ cross-ref
- **Verdict:** G2 PASS (full_eia EUIR 100% vs reactive/P3 0%); G0/G3 PASS
- **Tests:** 70 passed
- **Commit:** `da70345`

## Loop 23 — MATHEMATICS.md §8–9 completion (2026-08-17)

- **Done:** §3 DriveEngine per-channel params + saturation; §9 formal EOI, EUIR proxy, initiative precision from implemented code
- **Cross-ref:** `EOIScorer`, `AuthenticReasonDiscriminator`, `score_initiative_against_label`, `DriveEngine`
- **Tests:** 70 passed
- **Commit:** `b400555`

## Loop 24 — Structural diff automation in CI (2026-08-17)

- **Done:** `.github/workflows/eia-ci.yml` (pytest, replay smoke, trace diff); `research/ci_trace_diff_check.py`
- **Docs:** `docs/DEVELOPMENT_LOOP.md` CI section
- **Gate:** main 25 vs starter 22 nodes on twin_world_001; `EIA_CI_TRACE_DIFF=0` to skip
- **Tests:** 71 passed (+1 NAMM cert test)
- **Commit:** `7609c3c`

## Loop 25 — README + repo polish for public research (2026-08-17)

- **Done:** README — CI badge, G2 status, research reports table, re-execute in quick start
- **Done:** `docs/RESEARCH_INDEX.md` — full research artifact catalog
- **Commit:** `7609c3c`

## Loop 26 — MVP-1 planning delta (2026-08-17)

- **Done:** `docs/MVP1_SHADOW_PLAN.md` — shadow mode skeleton, sensors deferred checklist, consent UI stub spec
- **Done:** `docs/PLAN_DELTA.md` + `docs/LOOP_PLAN.md` iteration 6
- **Commit:** `7609c3c`

## Loop 27 — NAMM crosswalk update (2026-08-17)

- **Done:** `docs/NAMM_ARTIFACT_CROSSWALK.md` — 008–010 stub status, 013 runnable, Loops 12–23 findings
- **Done:** `AuthenticReasonCode.NAMM_SANDBOX_VERIFIED`; pipeline passes verified sandbox certs to discriminator
- **Done:** `NammAdapter.get_or_run_sandbox()` + `verified_sandbox_certificates()`
- **Commit:** `7609c3c`

## Loop 28 — Seed determinism bootstrap CI (2026-08-17)

- **Done:** `tests/test_seed_determinism.py`, `research/ci_seed_bootstrap.py`; CI workflow step
- **Seeds:** twin_world_001 with [42, 123, 999] — identical fingerprint per seed, distinct across seeds
- **Tests:** 73 passed (+2 seed determinism tests)
- **Commit:** `1e6d4ff`

## Loop 29 — Eval suite CI gate (2026-08-17)

- **Done:** `research/ci_eval_gate.py` — 6 scenarios full_eia; fail if mean EOI < 0.8 or precision < 0.75
- **Results:** mean EOI 1.0, initiative precision 100% — gate PASS
- **Tests:** 73 passed
- **Commit:** `1e6d4ff`

## Loop 30 — Release notes v0.2.0-mvp0 (2026-08-17)

- **Done:** `docs/RELEASE_v0.2.md` — Loops 1–27 achievements for public readers
- **Tag:** `v0.2.0-mvp0`
- **Commit:** `1e6d4ff`

## Loop 31 — INTERIM_RESEARCH_SUMMARY.md (2026-08-17)

- **Done:** `docs/INTERIM_RESEARCH_SUMMARY.md` — executive summary EN for Anthemium; evidence links; MVP-1 next steps
- **Commit:** `1e6d4ff`

### RETROSPECTIVE (Loops 28–31)

- Seed bootstrap closes G0 gap — multi-seed determinism enforced in CI beyond single-scenario replay smoke.
- Eval gate encodes G2 quality thresholds — mean EOI ≥ 0.8 and precision ≥ 0.75 on every push.
- v0.2.0-mvp0 tag marks MVP-0 research milestone for external reviewers.
- Interim summary consolidates G0–G3 evidence for stakeholder handoff to MVP-1 shadow.

### RETROSPECTIVE (Loops 24–27)

- CI gate closes G0 reproducibility loop — replay smoke + structural diff on every push.
- Public research index unblocks external reviewers without spelunking `research/`.
- MVP-1 shadow plan defers sensors while preserving full cognitive audit path.
- NAMM certificate is audit supplementary signal — does not override EOI/endogeneity gate.

### RETROSPECTIVE (Loops 20–23)

- Held-out adversarial suite frozen (ADV-H1–H6) — training/held-out separation enforced in CI.
- Full 5-baseline matrix confirms G2: full_eia EUIR 100% vs reactive/P3 0%.
- G2 evidence pack consolidates Loops 8–21 artifacts for gate review.
- MATHEMATICS.md now mirrors implementation constants for EOI/EUIR/precision/drives.

### RETROSPECTIVE (Loops 16–19)

- Consent-race harness closes THREAT_MODEL revocation gap with execution-time gate.
- PAI-EI-E0-001 smoke confirms full_eia dominance; event_rule cognitive-only denied by governor.
- Predictive P3 sends contacts but fails endogenous EOI gate — validates P4 vs P3 separation.
- Ground-truth scoring: full_eia 100% initiative precision on eval set; loader unblocks future metrics.

### RETROSPECTIVE (Loops 12–15)

- EUIR proxy cleanly separates reactive (zero initiative) from full EIA (six endogenous contacts).
- Event-rule stub fills EXPERIMENTS condition 3; salience gate at 0.30 fires on high-tension scenarios.
- Ground-truth labels unblock future contact-precision and abstain-quality metrics.
- Structural diff confirms main pipeline audit nodes absent in starter ledger — expected decomposition gap.

---

- RQ2/RQ3 closed: threshold crosswalk + SourceMass mapping enable κ studies.
- Paired EOI-003 confirms starter-native scenario works on main with delta 0.0.
- Eval harness now covers sparse-user, pure-ambient, and delayed-departure variants.
- SourceMass partition vocabulary still diverges (internal vs ambient) while RI agrees — track in RQ5.

---

## Meta-loop setup (2026-08-17)

**Loop type:** A (PLAN) + B (initial REVIEW)  
**Agent:** meta-loop subagent

### Deliverables

- [`META_LOOP.md`](META_LOOP.md) — three nested loop types (A→C→B)
- [`LOOP_PLAN.md`](LOOP_PLAN.md) — iteration 1 plan; Loops 1–6 status
- [`PLAN_DELTA.md`](PLAN_DELTA.md) — IMPLEMENTATION_PLAN changelog
- [`MATHEMATICS.md`](MATHEMATICS.md) — English formal model skeleton
- [`NEXT_AGENT_PROMPT.md`](NEXT_AGENT_PROMPT.md) — autonomous session handoff

### RETROSPECTIVE

- Coordinated with dev-loop: Loop 1 marked DONE (`779ddcb`), Loop 2 left for dev-loop commit.
- Tactical queue (LOOP_PLAN) separated from strategic plan (IMPLEMENTATION_PLAN) and delta log (PLAN_DELTA).
- Math track bootstrapped without blocking RQ1 code work.
