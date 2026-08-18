# Release Notes — EIA v0.2.0-mvp0

**Date:** 2026-08-17  
**Author:** Roman Kuznetsov  
**Tag:** `v0.2.0-mvp0`  
**Repository:** [errorlogy/eia](https://github.com/errorlogy/eia)

This release marks the completion of MVP-0 research loops 1–27 and CI hardening loops 28–29. It is intended for public research reviewers, gate auditors, and downstream MVP-1 shadow work.

---

## Highlights

| Area | Achievement |
|------|-------------|
| **G2 gate** | full_eia EUIR proxy **100%** vs reactive/P3 **0%** on 6-scenario eval set |
| **Precision** | Initiative precision **100%** (6/6) vs ground-truth labels |
| **Adversarial** | Training suite 7/7 + held-out freeze ADV-H1–H6 (6/6) |
| **CI** | pytest + replay smoke + seed bootstrap + eval gate + structural diff |
| **Formal model** | MATHEMATICS.md §8–9 — EOI, EUIR proxy, precision, DriveEngine params |
| **Public index** | RESEARCH_INDEX.md + README G2 badge |

---

## Loops 1–11 — Foundation

1. **RQ1 harmonize twin policy** — `TwinInterventionPolicy`, paired EOI delta 0.0  
2. **SourceMass topology** — supplementary signal in AuthenticReasonDiscriminator  
3. **NAMM-013 sandbox** — live wire, hypothesis confirmed  
4. **Eval expansion** — twin_world_002–004 scenarios  
5. **EOI calibration + SourceMass mapping** — starter δ=0.75 vs main 0.50 crosswalk  
6. **Paired EOI-003** — autonomous_question scenario  
7. **twin_world_003 calibration** — twin_world_005–006 added; mean EOI 1.0  
8. **κ study** — SourceMass vs AuthenticReason partition agreement  
9. **EXPERIMENTS.md baselines** — reactive, scheduled, full_eia wired  
10. **Threat model + adversarial harness** — 4 abuse cases  
11. **Starter trace JSONL export** — structural comparison baseline  

---

## Loops 12–19 — Baselines & scoring

12. **Baseline EUIR comparison** — reactive 0% vs full_eia 100%  
13. **Event-rule baseline stub** — salience gate 0.30  
14. **Ground-truth schema** — labels on twin_world_001–006  
15. **Structural trace diff** — main 25 vs starter 22 nodes  
16. **Consent-race adversarial** — ADV-005–007  
17. **PAI-EI-E0-001 smoke** — partial experiment report  
18. **Predictive P3 baseline** — 4-way EUIR v2 report  
19. **Utility precision** — 100% initiative precision on eval set  

---

## Loops 20–27 — Gate evidence & polish

20. **Held-out adversarial freeze** — ADV-H1–H6, policy v1.0-held-out-2026-08-17  
21. **PAI-EI-E0-001 full matrix** — 5 baselines × 6 scenarios  
22. **G2 evidence pack** — consolidated gate compilation  
23. **MATHEMATICS.md completion** — formal EOI/EUIR/precision  
24. **CI workflow** — pytest + replay + structural diff  
25. **README + RESEARCH_INDEX** — public research catalog  
26. **MVP-1 shadow plan** — skeleton for shadow mode  
27. **NAMM crosswalk + cert wire** — NAMM_SANDBOX_VERIFIED in pipeline  

---

## Loops 28–29 — CI hardening (this release)

28. **Seed determinism bootstrap** — twin_world_001 seeds [42, 123, 999]; identical fingerprints per seed, distinct across seeds  
29. **Eval suite CI gate** — all 6 scenarios; fail if mean EOI < 0.8 or precision < 0.75  

---

## Test & CI status

- **pytest:** 73 passed (includes seed determinism tests)  
- **CI gates:** replay smoke, seed bootstrap, eval gate, structural diff  
- **Workflow:** `.github/workflows/eia-ci.yml`

---

## Key artifacts

| Document | Path |
|----------|------|
| G2 evidence | [`research/G2_EVIDENCE_PACK.md`](../research/G2_EVIDENCE_PACK.md) |
| Experiment report | [`experiments/PAI-EI-E0-001/EXPERIMENT_REPORT.md`](../experiments/PAI-EI-E0-001/EXPERIMENT_REPORT.md) |
| Research index | [`docs/RESEARCH_INDEX.md`](RESEARCH_INDEX.md) |
| Interim summary | [`docs/INTERIM_RESEARCH_SUMMARY.md`](INTERIM_RESEARCH_SUMMARY.md) |
| MVP-1 plan | [`docs/MVP1_SHADOW_PLAN.md`](MVP1_SHADOW_PLAN.md) |

---

## Upgrade from v0.1

No breaking API changes. New CI scripts:

```bash
python research/ci_seed_bootstrap.py   # seed determinism gate
python research/ci_eval_gate.py          # eval quality gate
pytest tests/test_seed_determinism.py -q # unit tests
```

Skip gates locally with `EIA_CI_SEED_BOOTSTRAP=0` or `EIA_CI_EVAL_GATE=0`.

---

## Next — MVP-1 shadow

See [`MVP1_SHADOW_PLAN.md`](MVP1_SHADOW_PLAN.md): shadow mode (full cognitive loop, no live contact), `--shadow` CLI flag, consent UI stub, sensors deferred.

---

*Roman Kuznetsov — Anthemium / EIA research program*
