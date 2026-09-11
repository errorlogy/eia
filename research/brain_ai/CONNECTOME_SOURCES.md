# Connectome Sources (offline-first)

T-BRAIN-01..04 use a **synthetic or bundled tiny subgraph MVP** when real connectome exports are unavailable offline. Tier-0 / CI never load the full 166k-neuron MaleCNS graph.

## Active sources

| Source key | Status | Notes |
|------------|--------|-------|
| `bundled_tiny` | **active** | `data/tiny_subgraph.json` — default CI path |
| `synthetic` | **active** | Deterministic Erdős–Rényi in `connectome_export.py` |
| `google_male_cns` | **stub** | Offline ego-network at `data/google_male_subgraph.json` (gitignored) |
| `flywire_female` | **stub** | Offline ego-network at `data/flywire_female_subgraph.json` (gitignored) |

Configure via `config.yaml` → `connectome.source`.

## Google MaleCNS connectome (Sept 2026)

**What:** Complete male *Drosophila* central nervous system — brain + ventral nerve cord. ~166,700 neurons, ~125M synapses. Proofread, typed (11,710 types), with *fruitless*/*doublesex* dimorphism annotations.

**Relation to FlyWire female:** Complements the female FlyWire / FlyEM brain connectomes. MaleCNS adds VNC (body motor control) and enables male–female synaptic comparison (8,069 isomorphic, 138 dimorphic, 289 male-specific, 71 female-specific types per Cell paper). FlyWire v783 remains the reference for **female** adult brain; MaleCNS is the reference for **male** brain+CNS.

| Resource | URL |
|----------|-----|
| Google blog | https://research.google/blog/a-connectomics-milestone-mapping-the-complete-male-fruit-fly-brain/ |
| Cell paper | https://www.cell.com/cell/fulltext/S0092-8674(26)00942-6 |
| DOI | https://doi.org/10.1016/j.cell.2026.08.015 |
| Janelia project | https://www.janelia.org/project-team/flyem/male-cns-connectome |
| Portal + download | https://male-cns.janelia.org/ · https://male-cns.janelia.org/download/ |
| neuPrint dataset | `male-cns:v1.0` @ https://neuprint.janelia.org |
| Neuroglancer (standalone) | https://neuroglancer-demo.appspot.com/#!gs://flyem-male-cns/v1.0/male-cns-v1.0.jso |
| Bulk GCS prefix | `gs://flyem-male-cns/v1.0/` (flat-connectome, segmentation, neo4j DB) |
| License | CC-BY |

**EIA stack role (tier C, observational):** MaleCNS subgraph → spike dynamics → `OmegaWaveState` / OMEGA_t → T-BRAIN-03 shadow bridge → T-BRAIN-04 carryover. No biological identity or AGI* claims (`claim_allowed=false`, C2 ceiling).

## FlyWire female (deferred full export)

| Resource | URL |
|----------|-----|
| FlyWire / codex | https://flywire.ai/ |
| neuPrint (female) | `flyem-optic-lobe` / whole-brain releases per FlyWire docs |
| v783 reference | Deferred — requires network + FlyWire credentials for live API |

Offline ego-network export path mirrors MaleCNS: place JSON under `data/flywire_female_subgraph.json`.

## Neuraxon crosswalk

Neuraxon export remains **crosswalk only** — see `research/sci_flow/M-MO_do_o_arms_2026-09-02.json`.

## Offline policy

- No live API calls in tier-0 or CI.
- `connectome_export.load_subgraph(connectome_source=...)` falls back to deterministic synthetic when gitignored exports are absent.
- Full connectome bulk download is **opt-in local only** — see `data/README.md`.
- Subgraph exports should target **hundreds of neurons max** (ego-network / typed circuit), not 166k nodes.

## T-BRAIN-05 (planned)

Parity harness: same spike→OMEGA→shadow pipeline on `google_male_cns` vs `flywire_female` vs `synthetic` subgraphs; compare OMEGA_t span and bridge genesis coupling under matched seeds. Spec in `README.md`.
