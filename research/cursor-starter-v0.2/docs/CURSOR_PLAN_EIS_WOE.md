# Cursor Development Plan — EIS/WoE v0.2 → v0.3

## Порядок чтения

1. `AGENTS.md`
2. `.cursor/rules/eia.mdc`
3. `docs/ENDOGENOUS_INITIATIVE_SPECTRUM.md`
4. `docs/WINDOW_OF_EMERGENCE.md`
5. `docs/RESEARCH_PROTOCOL_EIS_WOE.md`
6. `docs/THREAT_MODEL.md`

Перед любым изменением: `make check && make woe`.

## Milestone A — causal receipts для WoE

Цель: превратить compact simulation output в event-sourced trace.

- добавить typed nodes для target tension, phase sample, WoE state, intent;
- записывать digest, parents, model/policy/config versions;
- не хранить raw sensitive features;
- добавить `why_now_receipt`;
- тест: natural-language rationale не может иметь parents, отсутствующие в ledger;
- тест: phase intervention меняет ожидаемые causal descendants.

Definition of done: `CognitiveTopology` измеряет WoE intent без special-case.

## Milestone B — bitemporal world/self model

- valid time и transaction time;
- source authority и confidence;
- historical policy replay;
- separate observed fact vs inferred state;
- expiry для affect/self-prior inference;
- тест counterfactual по policy, действовавшей в момент formation.

## Milestone C — learned target field

- заменить ручные weights calibration layer;
- input: posterior variance, residuals, staleness, learning progress, self mismatch;
- hard prohibit reward from engagement/contact count;
- train only target ranking, не governor;
- compare against Telogenesis-style linear priority;
- report calibration and out-of-domain failure.

## Milestone D — sparse delayed coherence graph

- typed module graph вместо all-to-all coupling;
- learned or designed delays;
- local order parameters и cluster detection;
- cross-frequency experiment без biological claims;
- detect symmetric phase clusters, которые global (R\) путает с incoherence;
- phase/coupling ablation across 100+ seeds.

## Milestone E — goal construction sandbox

- separate target, motive, goal, plan, action ticket;
- compositional goal grammar;
- novelty evaluator outside proposer;
- immutable constitution;
- capability-free shadow mode;
- EIS-7 only after passing novelty and boundedness tests.

## Milestone F — Contact Governor integration

- convert `EmergentIntent` into typed `InitiativeProposal`;
- preserve causal parents;
- ASK/NOTIFY require consent, budget, quiet-hours and trajectory risk;
- channel disabled by default;
- denial preserves the internal trace;
- no automatic ACT.

## Milestone G — evaluation harness

- factorial configurations;
- seed sweeps;
- survival curves for time-to-intent;
- false initiative rate;
- state-intervention sensitivity;
- EOI + ECS;
- JSONL experiment receipts;
- reproducible report generator.

## Запрещённые shortcuts

- `if coherence > x: send_message()`;
- скрытый system prompt «будь проактивным» как endogenous mechanism;
- считать random output эндогенной причиной;
- использовать 42 Hz как hard-coded certification condition;
- обучать governor вместе с proposer;
- называть EIS-6 сознанием;
- включать external tools до shadow evaluation;
- позволять memory maintenance менять constitution/consent/capabilities.

## Первый coding prompt

Используйте файл `prompts/CURSOR_MASTER_PROMPT_V0.2.md`. После его выполнения
переходите только к одному milestone за pull request.

