# Connectome Sources (offline-first)

T-BRAIN-01 uses a **synthetic subgraph MVP** when real FlyWire exports are unavailable offline.

## Planned sources

| Source | Status | Notes |
|--------|--------|-------|
| FlyWire v783 (Drosophila) | deferred | Requires network + FlyWire API credentials |
| Bundled tiny adjacency | **active** | `data/tiny_subgraph.json` or inline synthetic in harness |
| Neuraxon export | crosswalk only | See `research/sci_flow/M-MO_do_o_arms_2026-09-02.json` |

## Offline policy

- No live API calls in tier-0 or CI.
- `connectome_export.load_subgraph()` falls back to deterministic synthetic graph.
- Real exports may be placed under `data/` (gitignored except stubs).
