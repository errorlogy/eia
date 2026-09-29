"""Tick 83: non-circular version of tick 82. Gating blocks = consensus of the 4 original subjects; evaluated only on the
3 held-out subjects (211619, 213522, 377451). Per subject: empirical residual profile vs model profiles (plain vs
gated+homotopic), 3 model seeds each; Pearson r over the 7 modules."""
import numpy as np
from scipy.stats import pearsonr
import brain_eia as b
from tick14_boundaries import louvain
from tick20_crossval import labels_of, gate
from tick38_homotopic import H
from tick81_initiators_7subj import load
from tick82_model_initiators import sim, residual_profile

HELD = ["211619", "213522", "377451"]
mods = ["BG", "DMN", "SMA", "SAL", "FPN", "VAL", "SEN"]
co = sum((labels_of(x)[:, None] == labels_of(x)[None, :]).astype(float) for x in b.SUBJECTS) / 4
np.fill_diagonal(co, 0); cons = louvain(co, 1.0, 21)
a0 = np.full(94, -0.02)
print(f"{'subject':<9}{'variant':<17}" + "".join(f"{m:>8}" for m in mods) + "   r vs own empirical")
rs = {"plain": [], "gated+homotopic": []}
for s in HELD:
    C, tc = load(s); emp = residual_profile(C, tc); e = [emp[m] for m in mods]
    print(f"{s:<9}{'empirical':<17}" + "".join(f"{x:>+8.3f}" for x in e))
    for name, Ce in (("plain", C), ("gated+homotopic", gate(C + 0.05 * H, cons))):
        prof = np.mean([[residual_profile(C, sim(Ce, a0, 900 + k))[m] for m in mods] for k in range(3)], 0)
        r = pearsonr(prof, e)[0]; rs[name].append(r)
        print(f"{'':<9}{name:<17}" + "".join(f"{x:>+8.3f}" for x in prof) + f"   {r:+.2f}", flush=True)
print("mean r:", {k: round(float(np.mean(v)), 2) for k, v in rs.items()})
