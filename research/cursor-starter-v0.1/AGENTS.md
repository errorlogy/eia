# Instructions for coding agents

Scope work to the milestone requested by the user.

Before editing:

1. Read README.md.
2. Read .cursor/rules/eia.mdc.
3. Read the architecture/math/threat document relevant to the change.
4. Run make check.

After editing:

1. Add unit, counterfactual and negative-control tests where relevant.
2. Run make check and the affected CLI demo.
3. Summarize changed contracts and safety consequences.
4. Do not claim production readiness.

Critical invariants:

- no direct model-to-action;
- typed state is source of truth;
- proposer and governor are independent;
- abstain is always available;
- causal trace is mandatory;
- consent/capability are deny-by-default;
- EOI is causal request-independence, not consciousness.

