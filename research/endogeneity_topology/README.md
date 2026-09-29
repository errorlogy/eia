# Endogeneity × Topology

Exploratory strand (2026-09-29): how network topology shapes **endogenous initiative** at
X_trigger = 0. Hypothesis-generation mode — toy models, no claim-ladder framing.

| Folder | What |
|---|---|
| [`toy/`](toy/) | N EIA-like drive units (spec §7.2) + uncertainty aging + noise + neighbour coupling on synthetic graphs. Iteration log: [`toy/LOG.md`](toy/LOG.md) |
| [`eia_prototype/`](eia_prototype/) | `PopulationDriveEngine`: EIA-compatible drive engine built from the toy findings (populations per drive, aging+noise, μ, lateral inhibition). Demo: `tick29_demo.py` |
| [`human_connectome/`](human_connectome/) | Stuart–Landau whole-brain model on HCP DTI connectomes (AAL2, 4 subjects) with an EIA initiative readout. Summary: [`human_connectome/RESULTS.md`](human_connectome/RESULTS.md) |

## Run

```powershell
python research/endogeneity_topology/toy/topo_endo.py 0.2 0.6 1.0
cd research/endogeneity_topology/toy; python tick7.py          # ticks import topo_endo / tick6 from cwd

python research/endogeneity_topology/human_connectome/fetch_hcp.py   # data/ is gitignored
cd research/endogeneity_topology/human_connectome; python brain_eia.py; python control_e3.py; python hetero.py
```

Dependencies: numpy, scipy, networkx.

## Key findings

See **[`FINDINGS.md`](FINDINGS.md)** — consolidated claims with status (robust / holds / withdrawn / refuted) and concrete proposals for EIA.
