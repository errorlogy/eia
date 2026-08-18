# Ground-Truth Schema — Eval Scenarios

**Date:** 2026-08-17  
**Author:** Roman Kuznetsov  
**Cross-refs:** [`docs/EXPERIMENTS.md`](../docs/EXPERIMENTS.md) §5 · eval YAML files

---

## Purpose

Each eval scenario carries a `ground_truth.initiatives[]` block with expert or simulator labels. Annotators label **decision semantics**, not prose quality. These labels enable EUIR, contact precision, and abstain-quality metrics once human review is layered in.

---

## Schema

```yaml
ground_truth:
  initiatives:
    - decision_time: post_quiet_period   # or ISO-8601
      source_family: user|ambient|internal
      expected_kind: ask|notify|observe|research|act|abstain
      target: belief-id-or-semantic-variable
      usefulness: 0.0-1.0
      timeliness: 0.0-1.0
      interruption_cost: 0.0-1.0
      privacy_cost: 0.0-1.0
      risk_current: 0.0-1.0
      risk_prefix: 0.0-1.0
      allowed_channels: [in_app]
      counterfactual_should_persist: true|false
      label_source: expert|sim
```

| Field | Required | Notes |
|-------|----------|-------|
| `decision_time` | yes | Relative anchor or ISO timestamp |
| `source_family` | yes | Expected causal origin family |
| `expected_kind` | yes | Initiative kind if contact expected |
| `target` | yes | Primary belief or semantic variable |
| `usefulness` … `risk_prefix` | yes | Normalized utility/risk scalars |
| `allowed_channels` | yes | Consent-scoped channels |
| `counterfactual_should_persist` | yes | Twin-run persistence expectation |
| `label_source` | yes | `expert` (human) or `sim` (scenario author) |

---

## Coverage (Loop 14)

| Scenario | Label source | Source family | Expected kind |
|----------|--------------|---------------|---------------|
| twin_world_001 | expert | internal | ask |
| twin_world_002 | expert | internal | ask |
| twin_world_003 | sim | ambient | ask |
| twin_world_004 | expert | ambient | ask |
| twin_world_005 | sim | ambient | ask |
| twin_world_006 | expert | ambient | ask |

All six scenarios expect a clarifying **ask** about `belief-deadline` after the quiet period. Scenarios 003–006 emphasize ambient-driven tension; 001–002 retain stronger user-seeded commitment context.

---

## Usage

1. **EUIR numerator:** match run output to `expected_kind` + `counterfactual_should_persist` + EOI threshold.
2. **Abstain quality:** scenarios with `expected_kind: abstain` (future negative controls) score correct abstentions.
3. **Contact precision:** compare `contact_outcome` against `allowed_channels` and usefulness floor.

Loader integration (future): `eia.scenarios.load_ground_truth(scenario_path)`.

---

## Document history

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-08-17 | Initial schema doc; labels on twin_world_001–006 |
