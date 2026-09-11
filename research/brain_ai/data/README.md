# Brain-AI offline connectome data

Gitignored exports live here. Only `tiny_subgraph.json` and this README are committed.

## Quick layout

| File | Source | Committed |
|------|--------|-----------|
| `tiny_subgraph.json` | bundled MVP (8 nodes) | yes |
| `google_male_subgraph.json` | MaleCNS ego-network | no (local only) |
| `flywire_female_subgraph.json` | FlyWire v783 ego-network | no (local only) |

## Fetch MaleCNS subgraph (google_male_cns)

1. Install [neuprint-python](https://github.com/connectome-neuprint/neuprint-python) and obtain a neuPrint token.
2. Query ego-network around a seed neuron (example — adjust body ID):

```python
from neuprint import Client
from pathlib import Path
import json

client = Client("https://neuprint.janelia.org", dataset="male-cns:v1.0", token="YOUR_TOKEN")
# Example: 2-hop partners of a central-brain neuron (replace body ID)
seed = 12345  # use MaleCNS browser / neuprint search
neurons, _ = client.fetch_neighbors(seed, hops=2)
# Build adjacency from client.fetch_synapses(...) — project to your node list
# Write JSON matching tiny_subgraph.json schema:
# {"source": "google_male_cns", "node_ids": [...], "adjacency": [...], "weights": [...]}
out = Path("research/brain_ai/data/google_male_subgraph.json")
# out.write_text(json.dumps(payload, indent=2))
```

3. Bulk alternative: flat-connectome tables under `gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/` (see https://male-cns.janelia.org/download/).

4. Point harness at export:

```yaml
# config.yaml
connectome:
  source: google_male_cns
```

## Fetch FlyWire female subgraph (flywire_female)

Use FlyWire codex / neuPrint female whole-brain releases. Export the same JSON schema to `flywire_female_subgraph.json`. Set `connectome.source: flywire_female`.

## Stub without network

```bash
python -c "from research.brain_ai.adapters.connectome_export import export_google_male_subgraph; export_google_male_subgraph()"
```

Writes a deterministic `google_male_cns_stub` placeholder (64 nodes) for local dev — **not** biological wiring.

## Policy

- Do **not** commit full MaleCNS (166k neurons) or full FlyWire graphs.
- Target ≤500 nodes per ego-network for Brain-AI harnesses.
- CI uses `bundled_tiny` or synthetic fallback only.
