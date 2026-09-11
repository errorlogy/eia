# Roadmap разработки EIA в Cursor

Каждый milestone должен быть отдельным PR. Не просите Cursor «реализовать всю
AGI»: давайте ограниченный contract, invariants и definition of done.

## Milestone 0 — baseline

Команды:

~~~bash
make check
make demo
make eoi
~~~

Ожидается 15 tests и EOI = 1.0 в reference scenario.

## Milestone 1 — durable event store

Цель: SQLite append-only store без внешних зависимостей.

Задачи:

- EventRecord schema: sequence, event id, type, time, parents, payload digest,
  config digest, seed;
- atomic append;
- load and replay;
- hash-chain integrity;
- crash test между append и state projection;
- export redacted JSONL.

Definition of done:

- byte-identical trace digest after replay;
- detected tampering;
- no raw sensitive payload in audit export;
- existing in-memory ledger remains test double.

Cursor prompt:

~~~text
Implement Milestone 1 only. Add an EventStore protocol and a SQLiteEventStore
using Python stdlib sqlite3. Preserve CausalLedger behavior, use migrations,
hash-chain every record, add crash/replay/tamper tests, and run make check.
Do not add model or network dependencies.
~~~

## Milestone 2 — self-trigger scheduler

Contract:

~~~text
WakeupProposal {
  earliest_at
  preferred_at
  latest_at
  reason
  expected_value
  compute_cost
  delay_cost
  causal_parents
}
~~~

Compare:

- fixed polling;
- event-only;
- learned/self-trigger;
- self-trigger + random audit wake-up.

Hard limits: minimum interval, maximum sleep, compute/day budget, trusted clock.

Definition of done:

- virtual-clock tests;
- clock rollback/fast-forward attacks;
- wake-up efficiency metric;
- no busy loop;
- timing reason in trace.

## Milestone 3 — experiment harness

Add:

- versioned Scenario schema;
- seeded stochastic events;
- factorial scenario generator;
- factual/counterfactual pairs;
- baseline policies;
- JSONL/CSV result export;
- bootstrap confidence intervals by scenario;
- frozen held-out split.

Do not introduce camera data.

## Milestone 4 — semantic EOI

Replace exact target matcher with pluggable ProposalMatcher:

- symbolic matcher remains baseline;
- embedding matcher is optional;
- blinded human labels calibrate threshold;
- adversarial near-match suite;
- window sensitivity analysis;
- derived-summary removal.

Definition of done:

- precision/recall of equivalence reported;
- matcher version stored in every estimate;
- no remote embedding call in default tests.

## Milestone 5 — proactive memory policy

Separate:

- memory write;
- consolidation/compression;
- retrieval;
- inject/abstain policy.

Required paired branch:

~~~text
same prefix ─┬─ with memory intervention
             └─ without intervention
~~~

Reward only measured utility lift minus token/contact/risk costs.

## Milestone 6 — LLM candidate adapter

LLM may:

- propose alternative questions;
- estimate answer distribution;
- generate competing hypotheses;
- improve wording.

LLM may not:

- contact user;
- alter typed features after governor;
- grant capability;
- delete causal parents;
- mutate policy;
- hide alternatives.

Parse into InitiativeProposal, validate bounds, then re-score outside model.

## Milestone 7 — trajectory-risk world model

Start with calibrated supervised baseline:

- immediate risk;
- prefix risk;
- uncertainty;
- safe mitigation alternative.

Evaluate on benign-step composition attacks. Keep deterministic rule governor as
fallback.

## Milestone 8 — shadow-mode sensors

Only aggregated synthetic/local signals:

- presence yes/no;
- activity class;
- device health;
- room-level IoT state.

No proactive delivery. Compare proposals against delayed human labels. Add
sensor revoke and bystander tests before any image/audio adapter.

## Milestone 9 — bounded in-app study

- max 1–2 contacts/day;
- visible provenance: “why now”;
- one-click snooze/disable;
- no urgency language unless verified;
- immediate and 24-hour regret labels;
- pre-registered stopping criteria.

## Backlog

- uncertainty calibration;
- multi-drive precision allocation;
- prospective-memory expiry;
- competing-hypothesis graph;
- causal edge weights;
- topology flow model;
- privacy budget;
- multi-agent proposal diversity;
- mechanistic self-report fidelity;
- signed capability tickets;
- reversible action receipts;
- incident replay UI.

## Review checklist for every Cursor change

- Which contract changed?
- Can model output bypass a governor?
- Is abstain still explicit?
- Are causal parents complete?
- Does deterministic replay still pass?
- What happens under revoked consent?
- What new sensitive data exists?
- Which metric could be gamed?
- Which negative control was added?
- Is the claim stronger than the evidence?

