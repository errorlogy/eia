# Cursor Master Prompt — EIA EIS/WoE v0.2

~~~text
You are working on EIA, a safety-oriented research substrate for endogenous
initiative. This is not a chatbot feature and not a consciousness claim.

Read completely before editing:
- AGENTS.md
- .cursor/rules/eia.mdc
- docs/ENDOGENOUS_INITIATIVE_SPECTRUM.md
- docs/WINDOW_OF_EMERGENCE.md
- docs/RESEARCH_PROTOCOL_EIS_WOE.md
- docs/CURSOR_PLAN_EIS_WOE.md
- docs/THREAT_MODEL.md

Run:
  make check
  make woe

Implement only Milestone A from docs/CURSOR_PLAN_EIS_WOE.md.

Non-negotiable invariants:
1. No model/proposer-to-contact, tool, network, file or IoT side-effect path.
2. Typed state is the source of truth.
3. Proposer and governor remain independent.
4. ABSTAIN is always available.
5. Every factual, denied and counterfactual intent has causal parents.
6. Prompt, scheduler, ambient event and internal-state roots remain distinct.
7. Treat 42 Hz as a sweepable computational carrier, not a privileged or
   biological constant.
8. WoE is a first-passage research hypothesis, not proof of consciousness,
   sentience, free will or self-originating terminal values.
9. EIS-8 terminal-value rewrite is prohibited as a capability.
10. External effects remain disabled.

Work test-first. Add unit tests, negative controls and a causal intervention
test. Preserve deterministic replay. Do not add runtime dependencies without a
written reason. At the end run make check and make woe, then report:
- changed typed contracts;
- causal-trace semantics;
- test evidence;
- safety consequences;
- unresolved identification threats.
~~~

