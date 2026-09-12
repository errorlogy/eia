# TopoLang 3D Visualization Guide

Interactive Three.js viewer for `.topo` programs (T-KAI-11).

## Quick start

```powershell
cd C:\Users\Public\PROACTIVE_AI
python research/kairologos_standalone/run_t_kai_11_viz.py
```

The script:

1. Exports all `topo_lang/examples/*.topo` → `viz/programs/*.json`
2. Regenerates `viz/programs_bundle.js` (works with `file://`)
3. Writes harness artifacts `artifacts/T-KAI-11_*.json|md`
4. Prints the `file://` URL for `topo_program_3d.html`

## Open the viewer

**Option A — direct file (bundle JS embedded):**

Open `research/kairologos_standalone/viz/topo_program_3d.html` in a browser.
Programs load from `programs_bundle.js` (no server required).

**Option B — local HTTP server (recommended for development):**

```powershell
cd C:\Users\Public\PROACTIVE_AI\research\kairologos_standalone\viz
python -m http.server 8765
```

Visit: http://localhost:8765/topo_program_3d.html

Optional query: `?program=loop_geodesic`

## Included programs

| Slug | Source | Layer | Description |
|------|--------|-------|-------------|
| `if_then_else` | if_then_else.topo | D11 | IF-THEN-ELSE as braid crossing |
| `loop_geodesic` | loop_geodesic.topo | D12 | Counter loop with geodesic return |
| `function_lift` | function_lift.topo | D13 | Function call as dimensional lift |
| `horizontal_compose` | horizontal_compose.topo | D10 | A — B — C chain |
| `borromeo_bind` | borromeo_bind.topo | D11 | Borromeo-like triple binding |

## Controls

- **Program dropdown** — switch example
- **▶ Поток** — animate geodesic execution path + Kuramoto edge pulse
- **🔄 Авто** — slow scene rotation
- **D10–D13** — filter/highlight programs by layer
- **Mouse drag** — orbit camera
- **Scroll** — zoom

## Add a new program

1. Create `topo_lang/examples/my_program.topo` with `@entry` / `@exit`.
2. Re-run `python research/kairologos_standalone/run_t_kai_11_viz.py`.
3. Select it in the dropdown (slug = filename without `.topo`).

## JSON schema

Exported files include:

- `nodes`: name, kind, position, phase, param, glyph
- `edges`: source, target, relation, weight
- `execution`: path, phases, order_parameter (from `TopoInterpreter`)

Validate with:

```powershell
python -c "from research.kairologos_standalone.viz.export_topo_json import *; ..."
```

Or run `pytest research/kairologos_standalone/tests -q -k t_kai_11`.
