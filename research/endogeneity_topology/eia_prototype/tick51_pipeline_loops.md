# Tick 51 — causal loops in the MVP-0 architecture (static audit of `src/eia`)

Toy result A18/A19: collective endogeneity needs **closed causal loops with non-zero gain**; a DAG only
produces per-unit (clock-like) initiative. Here: which loops exist in the EIA code?

## Causal edges found in `src/eia`

| edge | where | notes |
|---|---|---|
| Observation → BeliefField | `sense_making/__init__.py:53–92` | the only regular writer of beliefs |
| BeliefField → DriveState | `drives/__init__.py` (`gradient_snapshot` → error term) | re-derived every compute (tick 32) |
| DriveState → DriveState | leaky integration `(1−ρ)d` | self-loop, gain < 1 |
| DriveState → Motivation → IntentionGenesis → Initiative | `pipeline.py:151`, `intention/__init__.py` | intensity acts as a gate (C4) |
| Initiative → ContactGovernor → decision | `pipeline.py` | terminal in `run_scenario` |
| Action → DriveState (satisfaction) | `drives/__init__.py:62–69` | **never used**: no caller passes `satisfaction` |
| Action → BeliefField (post-action update) | `runtime/shadow_multitick.py:235–258` | **only in shadow multitick**; writes a *fixed* belief (distribution 0.8/0.2, uncertainty 0.35) regardless of what the action was — the loop is closed structurally but its gain w.r.t. the action/drive state is **zero** |
| novelty input | `pipeline.py:143–147` | constant 0.15 / 0.20 after tick 2 — exogenous schedule, not state-dependent |

## Reading

- In `run_scenario` (all evals, PAI-EI-E0-001, G2 evidence) the architecture is a **DAG per episode**:
  Observation → Belief → Drive → Intention → Governor. The only cycle is the drive self-loop (gain 1−ρ < 1).
  By A18 this can yield only unit-level, clock-like initiative — consistent with C1 (drives pin or decay)
  and C6 (drive state causally inert where the field alone determines the initiative).
- `shadow_multitick` closes Action → Belief, but with a **content-free** update, so the loop gain is zero:
  the next cognition tick sees the same belief whatever the agent did. ATT-R "recurrence" evidence from this
  path therefore reflects a structural edge, not a dynamical loop.
- The satisfaction channel (Action → Drive) exists in the drive equation but is dead code in the pipeline.

## Proposals (extend FINDINGS D)

9. **Close the loops with state-dependent gain**: pass `satisfaction` from contact/answer outcomes into
   `DriveEngine.compute`; make post-action belief updates depend on the action and its target belief
   (e.g. resolve uncertainty of the targeted belief, as RESOLVE does in the toy — tick 10 showed this
   channel carries inter-motive influence).
10. **Keep the loop gain below 1 and sparse** (A19: 2–5 % recurrent edges give graded onset) and report
    the measured loop gain ρ of the cognitive cycle as an architectural metric alongside EOI.
11. Replace the constant novelty schedule with state-derived novelty (otherwise it is a hidden scheduler —
    identification threat #1 in MATHEMATICS.md §11).
