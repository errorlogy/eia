"""Heterogeneous local excitability along a unimodal->transmodal hierarchy proxy.
a_j: SEN -0.04 (damped), transmodal DMN/FPN/VAL -0.005 (near bifurcation), rest -0.02.
Re-fit threshold on the new intact model; then DMN vs strength-matched controls."""
import json, zlib
import numpy as np
import brain_eia as b

G = json.loads(open("results.json").read())["G_star"]
subj = {s: b.load(s) for s in b.SUBJECTS}
w = np.mean([b.peak_freqs(tc) for _, tc in subj.values()], axis=0)
a = np.full(94, -0.02)
a[b.IDX["SEN"]] = -0.04
a[np.concatenate([b.IDX["DMN"], b.IDX["FPN"], b.IDX["VAL"]])] = -0.005

_orig = b.simulate
def sim(C, w, G, rng, silence=None, **kw):
    # reuse integrator with vector a: patch via closure
    n = C.shape[0]; dt = 0.1; T = 900.0; sigma = 0.02
    av = a.copy()
    if silence is not None: av[silence] = -1.0
    omega = 2*np.pi*w; deg = C.sum(1)
    z = 0.1*(rng.standard_normal(n)+1j*rng.standard_normal(n))
    every = int(round(b.TR/dt)); xs=[]; env=[]; sq=np.sqrt(dt)*sigma
    for t in range(int(T/dt)):
        z = z + dt*((av+1j*omega)*z - np.abs(z)**2*z + G*(C@z-deg*z)) + sq*(rng.standard_normal(n)+1j*rng.standard_normal(n))
        if t % every == 0: xs.append(z.real.copy()); env.append(np.abs(z))
    return np.array(xs).T, np.array(env).T

pool = np.setdiff1d(np.arange(94), np.concatenate([b.IDX["DMN"], b.INIT_LOOP]))
k = len(b.IDX["DMN"])
envs, fit = {}, []
for s, (C, tc) in subj.items():
    x, envs[s] = sim(C, w, G, np.random.default_rng(zlib.crc32(repr((s,'h')).encode())))
    fit.append(np.corrcoef(b.fc(b.bandpass(tc)), b.fc(b.bandpass(x)))[0,1])
thr = float(np.percentile(np.concatenate([b.drive(e) for e in envs.values()]), 95))
def rate_of(sel_fn, tag):
    r, gd, gs = [], [], []
    for s, (C, _) in subj.items():
        env = envs[s] if sel_fn is None else sim(C, w, G, np.random.default_rng(zlib.crc32(repr((s,tag)).encode())), silence=sel_fn(C))[1]
        D = b.drive(env)
        r.append(b.timing_stats(b.initiatives(D, thr), env.shape[1])[0])
        gd.append(b.granger(env[b.IDX["DMN"]].mean(0), D)); gs.append(b.granger(env[b.IDX["SEN"]].mean(0), D))
    return {"rate_per_min": float(np.mean(r)), "GC_DMN": float(np.mean(gd)), "GC_SEN": float(np.mean(gs))}
out = {"FC_fit": float(np.mean(fit)),
       "intact": rate_of(None, "i"),
       "silence_DMN": rate_of(lambda C: b.IDX["DMN"], "d"),
       "silence_top_strength_16_nonDMN": rate_of(lambda C: pool[np.argsort(C.sum(1)[pool])[-k:]], "t"),
       "silence_random_16": rate_of(lambda C: np.random.default_rng(100).choice(pool, k, replace=False), "r"),
       "silence_SEN": rate_of(lambda C: b.IDX["SEN"], "s")}
print(json.dumps(out, indent=1)); json.dump(out, open("hetero.json","w"), indent=1)
