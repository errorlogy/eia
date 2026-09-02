# Research vendor dependencies

Third-party packages cloned for **sci-flow adjunct research** (Tier C explore). **Not** merged into `src/eia/` runtime. Claim ceiling **C2**; no AGI* claim.

| Package | Path | Source | Pinned commit | Role |
|---------|------|--------|---------------|------|
| **Neuraxon** | `neuraxon/` | [DavidVivancos/Neuraxon](https://github.com/DavidVivancos/Neuraxon) | `21eff5c` | Structural plasticity, multi-timescale synapses, recurrent loops |
| **Graphitti** | `graphitti/` | [UWB-Biocomputing/Graphitti](https://github.com/UWB-Biocomputing/Graphitti) | `b96e96c` | Growth-phase topology + STDP; endogenously active neurons |

Application map: [`../sci_flow/NEUROPLASTICITY_EIA_APPLICATION.md`](../sci_flow/NEUROPLASTICITY_EIA_APPLICATION.md).

---

## Neuraxon

**Language:** Python 3.8+  
**Dependencies:** none (core `neuraxon2.py` is pure Python; optional CUDA in `cuNxon/`)

```powershell
# Smoke (from repo root)
python research/sci_flow/smoke_vendor_neuroplasticity.py
```

**Manual import:**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("research/vendor/neuraxon")))
from neuraxon2 import NeuraxonNetwork, NetworkParameters

net = NeuraxonNetwork(NetworkParameters(num_input_neurons=3, num_hidden_neurons=5, num_output_neurons=2))
for _ in range(10):
    net.simulate_step()
```

**Install note:** cloned with `git clone --depth 1`; `.git` removed for monorepo vendor snapshot. Re-sync: re-clone and record new SHA here.

---

## Graphitti

**Language:** C++17  
**Build:** CMake ≥ 3.12; CPU default (`ENABLE_CUDA=NO`) or GPU (`ENABLE_CUDA=YES`)

```bash
cd research/vendor/graphitti/build
cmake -D ENABLE_CUDA=NO ..
make -j
./graphitti -c ../configfiles/test-tiny.xml
```

**Host status (2026-09-01):** clone verified; `cmake` not available on current Windows host — build deferred. Config smoke: `test-tiny.xml` + `ConnGrowth` + starter (endogenously active) neurons present in tree.

**Features relevant to EIA:** `ConnGrowth` (radius-based edge birth/death), `AllDynamicSTDPSynapses` (STDP weight dynamics), starter neurons with low `Vthresh` for spontaneous activity ([configuration docs](graphitti/docs/User/configuration.md)).

---

## Discipline

- Vendor code is **read/run in research** only; integration hypotheses use `do(O)` / shadow arms — see application doc.
- After substantive sci-flow edits: `python scripts/check_sci_tier0.py`.
