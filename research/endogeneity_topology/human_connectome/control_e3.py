"""E3 control: is the DMN silencing effect specific, or just 'remove 16 oscillators'?"""
import json, zlib
import numpy as np
import brain_eia as b

res = json.loads(open("results.json").read())
G, thr = res["G_star"], res["threshold"]
subj = {s: b.load(s) for s in b.SUBJECTS}
w = np.mean([b.peak_freqs(tc) for _, tc in subj.values()], axis=0)
pool = np.setdiff1d(np.arange(94), np.concatenate([b.IDX["DMN"], b.INIT_LOOP]))
k = len(b.IDX["DMN"])

def run(sel_fn, tag, draws):
    rates = []
    for d in range(draws):
        for s, (C, _) in subj.items():
            sel = sel_fn(C, d)
            _, env = b.simulate(C, w, G, np.random.default_rng(zlib.crc32(repr((s, tag, d)).encode())), silence=sel)
            rates.append(b.timing_stats(b.initiatives(b.drive(env), thr), env.shape[1])[0])
    return float(np.mean(rates)), float(np.std(rates))

strength = {s: C.sum(1) for s, (C, _) in subj.items()}
C0 = subj[b.SUBJECTS[0]][0]
st = C0.sum(1)
print("mean strength DMN %.3f | pool %.3f | loop %.3f" % (st[b.IDX['DMN']].mean(), st[pool].mean(), st[b.INIT_LOOP].mean()))
out = {
  "random_16": run(lambda C, d: np.random.default_rng(100 + d).choice(pool, k, replace=False), "rand", 3),
  "top_strength_16_nonDMN": run(lambda C, d: pool[np.argsort(C.sum(1)[pool])[-k:]], "top", 1),
  "FPN_8": run(lambda C, d: b.IDX["FPN"], "fpn", 1),
}
print(json.dumps(out, indent=1))
json.dump(out, open("control_e3.json", "w"), indent=1)
