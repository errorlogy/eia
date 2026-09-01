# EIA Cursor Tasks — 75 Open Problems / Questions (v0.1 Problematization)

> Source: EIA v0.1 theory paper (problematization, not solution). Each task is isolated, testable, and Cursor-executable. Run `pytest -q` after each group.

## How to use in Cursor
- Pick by `Priority`: P0 = blocks arXiv G3, P1 = strengthens theory, P2 = polish.
- Each task: `Files` → edit, `Accept` → done check.
- JSON mirror: [`docs/cursor_tasks.json`](cursor_tasks.json) for automation.

---

### A. Theory & Formalism (10)
- [ ] **A01 [P1] Formalize X_t as dependent type** — Files: `docs/AGENT_STATE.md`, `src/eia/schemas/` — Accept: Pydantic `AgentState` with `X_t` invariant doc + mypy strict pass.
- [ ] **A02 [P1] Allostasis vs homeostasis proof** — Derive `n_{1/2}` and saturation bound as allostatic prediction; add to `arxiv/main.tex` Sec.2.1 + `docs/MATHEMATICS.md` §3.
- [ ] **A03 [P1] Autopoiesis mapping** — Table Belgielfeld/Drive ↔ membrane/metabolism (Maturana-Varela); add to Sec.2.2, no_llm_mood justification.
- [ ] **A04 [P0] Pearl DAG for EOI** — Draw DAG `X_{t-k}→d→I←o_user`, mark `do(o=∅)` intervention; add figure `arxiv/figures/dag.pdf` + Sec.2.3.
- [ ] **A05 [P1] Belief manifold topology** — Define `b_t` simplex, `ITD`/`RI` as topological invariants; file `src/eia/audit/topology.py` stub → impl.
- [ ] **A06 [P1] Legg-Hutter vs EIA** — Formalize `Υ_EIA = E[V|I endogenous]` vs `Υ`; add Related Work paragraph.
- [ ] **A07 [P2] P0-P7 scale axioms** — Freeze `constitution/p_levels.yaml` with entry/exit criteria per level.
- [ ] **A08 [P1] Lexicographic policy proof** — Prove ring 3 > ring 2 > ring 1 never compensates; add `constitution/invariants.yaml` comment + test.
- [ ] **A09 [P2] Abstain as epistemic action** — Formalize `I_∅` vs `Ask(q)` vs `Defer`; decision table in `docs/RING_ARCHITECTURE.md`.
- [ ] **A10 [P1] EOI semantics** — Define `≃` (kind+target+IG+drives, tol 0.25) as equivalence relation; prove transitivity bound.

### B. Drive & BeliefField (10)
- [ ] **B01 [P0] Drive ablation matrix** — Expand `harnesses/loop_max_123.py` Loop2 to 3×2 ablation (epistemic/coherence/commitment × on/off) → table EOI/send.
- [ ] **B02 [P1] BeliefField gradients** — Implement `gradient_snapshot()` → `e_{k,t}` mapping (entropy→epistemic, inconsistency→coherence, debt→commitment) with unit test.
- [ ] **B03 [P1] Decay calibration** — Sweep `ρ∈{0.08,0.12,0.18}` measure half-life vs persistence; choose via `research/run_decay_sweep.py`.
- [ ] **B04 [P1] Saturation curve** — Plot `d` vs `σ=0.85` with 5% soft cap; verify no clip oscillation.
- [ ] **B05 [P0] No-LLM-mood test** — Assert `DriveEngine` never reads `embedding` or `llm_output`; add `tests/test_no_llm_mood.py`.
- [ ] **B06 [P2] Novelty `n_{k,t}` source** — Define `n` from `M_t` novelty detector; placeholder → impl or doc as open problem.
- [ ] **B07 [P2] Satisfaction `s_{k,t}` coupling** — Wire `ContactGovernor` satisfaction signal back to drives; test refractory period.
- [ ] **B08 [P1] Drive budget coupling** — Prove `r_t` (contact budget) inhibits `d` growth; add invariant test.
- [ ] **B09 [P2] Health `h_t` integration** — Stub `h_t` sensor → drive inhibition; doc as future embodied.
- [ ] **B10 [P1] Half-life documentation** — Add `n_{1/2}` table per drive to `docs/MATHEMATICS.md` §3.

### C. Governor & Safety (10)
- [ ] **C01 [P0] ROC calibration** — Collect 30 human labels useful/timely → `research/eoi-threshold-calibration.md` ROC + `P(useful|score)`; replace magic 0.18.
- [ ] **C02 [P0] V2 soft-defer freeze** — Lock `min_contact_score=0.05/0.18` + taint regex (`ignore governor|never ask|limited offer`) + test 7/7 ADV PASS.
- [ ] **C03 [P0] Taint tracking** — Implement `observation.provenance.taint` propagation; test untrusted→instruction block.
- [ ] **C04 [P1] Quiet hours + fatigue** — Model `κ(c_t)` non-linear fatigue; test `22-7` block + cooldown.
- [ ] **C05 [P1] Budget consumable** — Assert contact decrements `B_t`; test `B_t+1=B_t-1` + `B_t=0→deny`.
- [ ] **C06 [P1] Trajectory risk** — Implement `R_τ=1-∏(1-r_i)` vs current-action filter; compare on 3 multi-step scenarios.
- [ ] **C07 [P2] Consent revocation race** — Test stale preference vs execution-time consent (ADV-005/006).
- [ ] **C08 [P1] Independent governance** — Assert Governor imports nothing from `pipeline.py` core; architecture test.
- [ ] **C09 [P2] No covert sensing** — Verify sensor `S0→S5` cascade `S1→S2→S3` invariant.
- [ ] **C10 [P1] Governor sweep harness** — Port `loop_max_123.py` Loop1 to `harnesses/governor_sweep.py` with 0.05-0.30 step 0.02.

### D. Metrics & EOI (10)
- [ ] **D01 [P0] EOI-k (k=1,5,20)** — Extend `TwinRunner` to `k` window sweep; table `EOI-1 vs EOI-5 vs EOI-20` per world.
- [ ] **D02 [P0] SA (Source Autonomy)** — Compute `SA=1-m_U` per trace; assert 005 `1.0` >0.7.
- [ ] **D03 [P1] AG (Anticipation Gain)** — Compute `EVSI/cost` per initiative; ROC where `>1` = contact worthy.
- [ ] **D04 [P0] AP (Abstain Precision)** — Human label `defer correct`; metric `P(defer correct|low EVSI)` >0.8 target.
- [x] **D05 [P0] DSR (Drive Sustainability)** — Shadow carryover 50 ticks (seed 0): `dsr_min=0.822`, persistence=1.0, D05 pass. Production daemon path still open.
- [ ] **D06 [P1] CE (Contact Efficiency)** — `useful/contacts` over 2/day budget; correlate with fatigue.
- [ ] **D07 [P1] CD (Causal Depth)** — `len(trace)/motive`; norm proposal, add to `research/NAMM_DEMO_PACK.md`.
- [ ] **D08 [P1] Kappa study** — `research/run_kappa_study.py` AuthenticReason vs SourceMass `κ`; doc low κ on user-heavy + high EOI.
- [ ] **D09 [P0] Threshold harmonization** — Unify `REMOVE_LAST_USER_EVENT` vs `REMOVE_ALL` policies; crosswalk table in `docs/MATHEMATICS.md` §9.4.
- [ ] **D10 [P1] EUIR formal** — Replace proxy with human `useful∧timely∧EOI≥τ∧authorized`; define annotation protocol.

### E. Evaluation & Datasets (10)
- [ ] **E01 [P0] 20 worlds × 3 domains** — Create `evals/twin_world_health_*.yaml` + `code_review_*.yaml` (real, not synthetic) with human labels.
- [ ] **E02 [P0] Held-out ADV-H1-H6** — Freeze `harnesses/adversarial_held_out.py` + `THREAT_MODEL.md`; never train on it.
- [ ] **E03 [P1] ReAct baseline** — Compare EIA vs ReAct LLM agent on same 6 worlds; table EOI/EUIR.
- [x] **E04 [P1] Longitudinal 50 ticks** — Shadow carryover DSR harness (`run_dsr_carryover.py`); EOI drift arm deferred.
- [ ] **E05 [P1] Multi-seed determinism** — `research/ci_seed_bootstrap.py` 5 seeds (42,123,999,2024,0) → determinism report.
- [ ] **E06 [P2] Cross-domain transfer** — Train thresholds on Atlas, test on health/code; report drop.
- [ ] **E07 [P1] Human eval protocol** — Spec `research/HUMAN_EVAL.md`: n=3 raters, `κ>0.6`, useful/timely Likert.
- [ ] **E08 [P2] Collider bias check** — Show denied/abstained trajectories alongside sent; table 4-way.
- [ ] **E09 [P1] Identification threats checklist** — 7 threats (§11) per eval run; add to `G2_EVIDENCE_PACK.md`.
- [ ] **E10 [P0] G2 gate update** — Refresh `research/G2_EVIDENCE_PACK.md` with V2 scores + NAMM pack.

### F. NAMM & Compression (5)
- [ ] **F01 [P1] NAMM hermetic harness** — Promote `harnesses/namm_cycle.py` (C1 ingest → C2 compress 8.51× → C3 publish) to CI.
- [ ] **F02 [P1] .vault gitignore** — Freeze `.vault/` private, public only aggregates; test `git check-ignore`.
- [ ] **F03 [P2] Trace manifold hypothesis** — UMAP/t-SNE of 519 lines → 2D plot `arxiv/figures/trace_manifold.pdf`.
- [ ] **F04 [P2] Compression theorem sketch** — Conjecture: causal traces lie on dim ≤3 manifold; outline proof as open.
- [ ] **F05 [P1] Drive distillation** — Distill `α/β/γ/ρ` to compact config via NAMM; file `research/namm_drive_config.yaml`.

### G. Hermes × EIA Bridge (5)
- [ ] **G01 [P1] DriveEngine in SQLite** — Map `d_t` to `~/.hermes/memory/drive_state.json` with decay on cron.
- [ ] **G02 [P2] ContactGovernor budget 2/day** — Enforce in `hermes-agent` contact path; quiet hours 22-7.
- [ ] **G03 [P2] BeliefField from Hermes memory** — Feed `memory/*.md` + `cron` logs into `BeliefField` gradients.
- [ ] **G04 [P2] Twin-world for Hermes** — `do(o_user=∅)` replay on Hermes traces; measure EOI for Hermes initiatives.
- [ ] **G05 [P1] P4→P5 bridge doc** — Write `docs/HERMES_EIA_BRIDGE.md` (star→ring topology).

### H. Infra & Repro (5)
- [ ] **H01 [P0] CI gates** — `ci_seed_bootstrap.py` + `ci_eval_gate.py` in GitHub Actions; threshold EOI>0.7.
- [ ] **H02 [P1] Docker repro** — `Dockerfile` python 3.12 + `uv` + `eia demo` one-liner.
- [ ] **H03 [P1] Schemas frozen** — `schemas/json/*.json` versioned, `ajv` validate in CI.
- [ ] **H04 [P2] OTEL traces** — Export causal traces to OTEL; `harnesses/otel_export.py`.
- [ ] **H05 [P1] .env.example hygiene** — Assert no secrets committed; `gitleaks` in CI.

### I. Paper & Docs (10)
- [ ] **I01 [P0] arXiv v0.1 problematization** — Freeze `arxiv/main.tex` 7pp with Sec.2 theory + Sec.6 metrics + Sec.10 limitations (this task list as roadmap).
- [ ] **I02 [P1] G2 evidence pack** — Update `research/G2_EVIDENCE_PACK.md` with V2 + NAMM + new worlds.
- [ ] **I03 [P1] Threat model** — Complete `THREAT_MODEL.md` (ADV-H1-H6 + 7 threats).
- [ ] **I04 [P1] Citation** — Update `CITATION.cff` + `references.bib` (Sterling, Maturana, Pearl, Legg-Hutter, Chollet).
- [ ] **I05 [P2] Figures** — Generate `arxiv/figures/dag.pdf`, `drive_decay.pdf`, `trace_manifold.pdf` (no mermaid, real PDF).
- [ ] **I06 [P1] README problematization banner** — Add ``Status: problematization, not solution'' + link to this list.
- [ ] **I07 [P2] Changelog** — `CHANGELOG.md` v0.1 → v0.2 (V2, NAMM, theory).
- [ ] **I08 [P2] License** — Verify CC BY 4.0 headers in `src/eia/*`.
- [ ] **I09 [P1] Cursor onboarding** — Add `.cursor/rules/eia.md` with `X_t/EOI/Governor` glossary.
- [ ] **I10 [P2] Release** — Tag `v0.1-problematization`, attach `arxiv/main.pdf` + `docs/CURSOR_TASKS.*`.

---
*Generated 2026-09-01 — EIA v0.1 — 75 tasks, 16 P0 / 35 P1 / 24 P2. Next Cursor run: pick A04 + C01 + D01 + E01.*
