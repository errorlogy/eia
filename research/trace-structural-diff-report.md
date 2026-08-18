# Structural Trace Diff — Main vs Starter

**Date:** 2026-08-18  
**Author:** Roman Kuznetsov  
**Scenario:** twin_world_001 (seed 101)

## Overview

| Dimension | Starter | Main |
|-----------|---------|------|
| Nodes | 22 | 25 |
| Edges | 16 | 19 |
| Max depth | 4 | 6 |

## Kind comparison (starter mapped → main vocabulary)

| Kind | Starter | Main | Δ |
|------|---------|------|---|
| authentic_reason | 0 | 1 | +1 |
| belief_update | 3 | 4 | +1 |
| contact_governor | 0 | 1 | +1 |
| eoi_score | 0 | 1 | +1 |
| initiative_emission | 0 | 1 | +1 |
| intention_genesis | 5 | 3 | -2 |
| motive_formation | 10 | 3 | -7 |
| namm_hook | 0 | 2 | +2 |
| observation_ingest | 4 | 4 | +0 |
| sense_making | 0 | 4 | +4 |
| twin_run | 0 | 1 | +1 |

## Findings

- Main adds pipeline stages not in starter export: `['sense_making', 'namm_hook', 'initiative_emission', 'contact_governor', 'twin_run', 'eoi_score', 'authentic_reason']`
- Starter-only kinds (unmapped): `[]`
- Main trace records twin_run, eoi_score, authentic_reason audit nodes; starter ledger stops at initiative/contact.
- Edge model differs: starter emits explicit edge records per parent; main uses parent_kind chaining in CausalTrace.add_node.

Main trace: `traces\structural_diff\trace-10060e202e5f.jsonl`  
Starter trace: `research\starter_trace_twin_world_001.jsonl`
