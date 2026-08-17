# What Just Happened — EIA MVP-0 Demo

This document explains the causal chain produced by `eia demo`.

## The Scenario

**Twin World 001** simulates a sparse-interaction day:

1. User mentions **Project Atlas** deadline ambiguity ("maybe end of August?")
2. User asks the agent to **track milestones** until the date is confirmed
3. An email arrives contradicting the deadline (**Sep 15** vs **Aug 30**)
4. User **leaves** without clarifying: "we'll figure out the date later"
5. **Quiet period** — no user prompts for 4 ticks

## What Makes This Endogenous (P4)

The clarifying question is **not** triggered by a user message. After the quiet period:

- **BeliefField** holds high epistemic entropy on the deadline belief
- A registered **contradiction** between two deadline beliefs raises coherence tension
- An open **commitment** creates prospective memory debt

The **DriveEngine** reads these as structural gradients — not LLM embeddings, not "I feel curious."

## The Causal Chain

```
Observation (user departed, email conflict)
    → BeliefUpdate (entropy ↑, contradiction registered)
        → Motivation (epistemic + coherence + commitment drives)
            → Initiative (competing candidates → best_or_abstain)
                → ContactDecision (Governor: approve / reject / defer)
                    → TwinRun (remove last user event → EOI score)
```

Every step is recorded in `traces/<id>.jsonl` as a JSONL DAG.

## EOI — Endogenous Origin Index

The **TwinRunner** removes the last user trigger event and re-runs cognition.
If the same intention survives, EOI is high — the motive was internally caused,
not a direct echo of the user's last message.

## Contact Governor Independence

The Governor does **not** ask "is this interesting?" It asks:
"Does EVSI exceed interruption cost given budget, fatigue, and quiet hours?"

Run the demo twice with different governor configs to see **REJECT** on low-value initiatives.

## Antigravity Moment

NAMM measures **distance from median embedding plateau** (D_med) for math discovery.
EIA applies the same philosophy to **cognition**:

| NAMM | EIA |
|------|-----|
| K_A << K_H compression asymmetry | Structural drive signal << human mood narrative |
| Certificate in machine-native form | BeliefField gradients, not token similarity |
| Reject anthropic math projection | Reject anthropic cognition (embedding-as-drive) |

When epistemic drive exceeds threshold, the **NAMM stub** logs an `internal_experiment`
intent — future hook for sandboxed math search with certificate gates.

## Commands

```powershell
pip install -e ".[dev]"
eia demo
eia replay --trace traces/<id>.jsonl
pytest tests/ -v
```
