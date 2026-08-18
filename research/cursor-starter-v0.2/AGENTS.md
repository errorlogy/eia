# Instructions for coding agents

Scope work to the milestone requested by the user.

Before editing:

1. Read README.md.
2. Read .cursor/rules/eia.mdc.
3. Read the architecture/math/threat document relevant to the change.
4. Run make check.
5. For EIS/WoE work, read docs/ENDOGENOUS_INITIATIVE_SPECTRUM.md and
   docs/WINDOW_OF_EMERGENCE.md, then run make woe.

After editing:

1. Add unit, counterfactual and negative-control tests where relevant.
2. Run make check and the affected CLI demo.
3. Summarize changed contracts and safety consequences.
4. Do not claim production readiness.
5. For WoE changes, run zero-tension, phase-scrambling and carrier-sweep controls.

Critical invariants:

- no direct model-to-action;
- typed state is source of truth;
- proposer and governor are independent;
- abstain is always available;
- causal trace is mandatory;
- consent/capability are deny-by-default;
- EOI is causal request-independence, not consciousness.
- 42 Hz is a sweepable carrier parameter, not a privileged or biological constant.
- EIS-8 terminal-value rewrite is prohibited as a capability.
