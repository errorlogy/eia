
## 📊 NeuraxonLife2-1M Dataset ( Regular + Full Version)

**NEW**: We've released a comprehensive dataset of 1M+ evolved neural networks from our artificial life simulations!
Update 12/10/25: Added A Full version to include also each full game info captured check NeuraxonLife2-1MFull_manifest.json at HuggingFace data repor for details

<a href="https://huggingface.co/datasets/DavidVivancos/NeuraxonLife2-1M"><img src="https://img.shields.io/badge/🤗%20Dataset-HuggingFace-orange"></a>

The **NeuraxonLife2-1M Dataset** contains detailed simulation data capturing:
- 🧠 Complete neural architectures and synaptic connectivity
- ⚡ Multi-timescale synaptic weights (fast, slow, meta)
- 🧬 Neuromodulation states (dopamine, serotonin, acetylcholine, norepinephrine)
- 📈 Behavioral performance and fitness metrics
- 🌳 Dendritic branch computation data

### Dataset Structure

| Table | Description | Key Data |
|-------|-------------|----------|
| `nxers.parquet` | Agent-level data | Neural parameters, fitness scores, lineage |
| `neurons.parquet` | Neuron-level data | Membrane potentials, phases, health |
| `synapses.parquet` | Synapse-level data | Multi-timescale weights, delays, plasticity |
| `branches.parquet` | Dendritic branches | Branch potentials, plateau dynamics |

### Quick Start
```python
from datasets import load_dataset

# Load from Hugging Face Hub
dataset = load_dataset("DavidVivancos/NeuraxonLife2-1M")

# Or with pandas
import pandas as pd
nxers = pd.read_parquet('neuraxonLife2-1M_nxers.parquet')
```

### Research Applications

- **Fitness Prediction**: Predict agent fitness from neural parameters
- **Evolutionary Dynamics**: Track neural evolution across generations
- **Network Topology Analysis**: Study evolved architectures
- **Neuromodulation Research**: Investigate modulator dynamics
- **Synaptic Weight Distribution**: Analyze learned connection patterns

👉 [**Explore the full dataset on Hugging Face**](https://huggingface.co/datasets/DavidVivancos/NeuraxonLife2-1M)
