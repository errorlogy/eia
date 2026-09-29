"""Human-connectome EIA model (toy, X_trigger = 0).

Substrate: HCP structural connectomes (DTI, AAL2 94 regions, 4 subjects, via
neurolib's public dataset) + resting-state fMRI for validation.

Dynamics: Stuart-Landau (Hopf) whole-brain model (Deco et al. 2017)
    dz_j = [(a + i w_j) z_j - |z_j|^2 z_j + G sum_k C_jk (z_k - z_j)] dt + s dW + I_j dt
a < 0 slightly: every region is a damped oscillator kicked by noise; long-range
coupling G sets how close the whole network is to collective oscillation.

EIA mapping (AAL2 -> functional module):
    DMN   internal generator Z      medial PFC, PCC, precuneus, angular, hippocampal
    SAL   "why now" / contact gate  insula, anterior cingulate
    BG    action governor gate      caudate, putamen, pallidum, thalamus
    SMA   initiation (readiness)    SMA, mid-cingulate
    VAL   drives / value            OFC, rectus, amygdala
    FPN   executive intention       mid/inf frontal, inf parietal, supramarginal
    SEN   exogenous channel X       visual, auditory, somatosensory

Initiative readout: initiation-loop drive D(t) = mean envelope of SAL+BG+SMA.
An initiative = upward crossing of a threshold fixed on the intact brain at the
operating point, with 5 s refractory. Threshold is NOT re-fitted per condition.

Experiments
    E1 fit G: sim FC vs empirical rs-FC
    E2 initiative rate / timing vs G (criticality)
    E3 do(Z): silence DMN vs silence SEN vs stimulate SEN (exogenous control)
    E4 topology: degree-preserving rewire (kills modularity) vs intact
    E5 attribution: linear Granger DMN->D vs SEN->D at X = 0
"""

from __future__ import annotations

import json
import zlib
from pathlib import Path

import numpy as np
import scipy.io as sio
from scipy.signal import butter, filtfilt

HERE = Path(__file__).parent
DATA = HERE / "data"
SUBJECTS = ["101309", "102311", "102816", "131217"]
TR = 0.72

AAL2 = """Precentral Frontal_Sup_2 Frontal_Mid_2 Frontal_Inf_Oper Frontal_Inf_Tri
Frontal_Inf_Orb_2 Rolandic_Oper Supp_Motor_Area Olfactory Frontal_Sup_Medial Frontal_Med_Orb
Rectus OFCmed OFCant OFCpost OFClat Insula Cingulate_Ant Cingulate_Mid Cingulate_Post
Hippocampus ParaHippocampal Amygdala Calcarine Cuneus Lingual Occipital_Sup Occipital_Mid
Occipital_Inf Fusiform Postcentral Parietal_Sup Parietal_Inf SupraMarginal Angular Precuneus
Paracentral_Lobule Caudate Putamen Pallidum Thalamus Heschl Temporal_Sup Temporal_Pole_Sup
Temporal_Mid Temporal_Pole_Mid Temporal_Inf""".split()
LABELS = [f"{n}_{h}" for n in AAL2 for h in "LR"]  # AAL2 order: L,R pairs, 94 regions

MODULES = {
    "DMN": ["Frontal_Sup_Medial", "Frontal_Med_Orb", "Cingulate_Post", "Precuneus", "Angular",
            "Hippocampus", "ParaHippocampal", "Temporal_Mid"],
    "SAL": ["Insula", "Cingulate_Ant"],
    "BG": ["Caudate", "Putamen", "Pallidum", "Thalamus"],
    "SMA": ["Supp_Motor_Area", "Cingulate_Mid"],
    "VAL": ["OFCmed", "OFCant", "OFCpost", "OFClat", "Rectus", "Amygdala"],
    "FPN": ["Frontal_Mid_2", "Frontal_Inf_Tri", "Parietal_Inf", "SupraMarginal"],
    "SEN": ["Calcarine", "Cuneus", "Lingual", "Occipital_Sup", "Occipital_Mid", "Occipital_Inf",
            "Heschl", "Postcentral", "Temporal_Sup"],
}
IDX = {m: np.array([i for i, l in enumerate(LABELS) if l.rsplit("_", 1)[0] in names])
       for m, names in MODULES.items()}
INIT_LOOP = np.concatenate([IDX["SAL"], IDX["BG"], IDX["SMA"]])


def load(subj: str):
    sc = sio.loadmat(DATA / f"{subj}_DTI_CM.mat")["sc"].astype(float)
    tc = sio.loadmat(DATA / f"{subj}_TC_rsfMRI_REST1_LR.mat")["tc"].astype(float)
    np.fill_diagonal(sc, 0)
    sc = (sc + sc.T) / 2
    return sc / sc.max() * 0.2, tc


def bandpass(x, lo=0.01, hi=0.1, fs=1 / TR):
    b, a = butter(2, [lo / (fs / 2), hi / (fs / 2)], btype="band")
    return filtfilt(b, a, x, axis=-1)


def peak_freqs(tc):
    x = bandpass(tc, 0.04, 0.07)
    f = np.fft.rfftfreq(x.shape[1], TR)
    p = np.abs(np.fft.rfft(x, axis=1)) ** 2
    band = (f >= 0.04) & (f <= 0.07)
    return f[band][np.argmax(p[:, band], axis=1)]


def fc(x):
    c = np.corrcoef(x)
    return c[np.triu_indices_from(c, 1)]


def simulate(C, w, G, rng, T=900.0, dt=0.1, a=-0.02, sigma=0.02,
             silence=None, stim=None, stim_amp=0.0):
    n = C.shape[0]
    a_vec = np.full(n, a)
    if silence is not None:
        a_vec[silence] = -1.0  # strongly damped: region cannot self-oscillate
    I = np.zeros(n)
    if stim is not None:
        I[stim] = stim_amp
    omega = 2 * np.pi * w
    deg = C.sum(1)
    z = 0.1 * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    steps = int(T / dt)
    every = int(round(TR / dt))
    xs, env = [], []
    sq = np.sqrt(dt) * sigma
    for t in range(steps):
        coup = G * (C @ z - deg * z)
        z = z + dt * ((a_vec + 1j * omega) * z - (np.abs(z) ** 2) * z + coup + I) \
            + sq * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
        if t % every == 0:
            xs.append(z.real.copy())
            env.append(np.abs(z))
    return np.array(xs).T, np.array(env).T  # (n, time) sampled at TR


def drive(env):
    return env[INIT_LOOP].mean(0)


def initiatives(D, thr, refr_s=5.0):
    refr = int(refr_s / TR)
    ev, last = [], -10**9
    for t in range(1, len(D)):
        if D[t - 1] < thr <= D[t] and t - last >= refr:
            ev.append(t)
            last = t
    return np.array(ev)


def timing_stats(ev, n_t):
    rate = len(ev) / (n_t * TR / 60)  # per minute
    if len(ev) > 3:
        isi = np.diff(ev)
        cv = isi.std() / isi.mean()
    else:
        cv = float("nan")
    return rate, cv


def granger(src, dst, p=3):
    """ln(var(dst|dst past)/var(dst|dst past, src past)), linear, lag p."""
    n = len(dst)
    Y = dst[p:]
    own = np.column_stack([dst[p - k: n - k] for k in range(1, p + 1)])
    ext = np.column_stack([src[p - k: n - k] for k in range(1, p + 1)])
    one = np.ones((len(Y), 1))
    r1 = Y - np.hstack([one, own]) @ np.linalg.lstsq(np.hstack([one, own]), Y, rcond=None)[0]
    X2 = np.hstack([one, own, ext])
    r2 = Y - X2 @ np.linalg.lstsq(X2, Y, rcond=None)[0]
    return float(np.log(r1.var() / r2.var()))


def rewire(C, rng, swaps=20):
    """Weighted degree-preserving-ish rewire: Maslov-Sneppen on binarised edges, weights shuffled."""
    A = C.copy()
    n = A.shape[0]
    edges = np.array(np.triu_indices(n, 1)).T
    edges = edges[A[edges[:, 0], edges[:, 1]] > 0]
    wts = A[edges[:, 0], edges[:, 1]].copy()
    E = [tuple(e) for e in edges]
    Es = set(E)
    for _ in range(swaps * len(E)):
        i, j = rng.integers(len(E), size=2)
        (a, b), (c, d) = E[i], E[j]
        if len({a, b, c, d}) < 4:
            continue
        e1, e2 = tuple(sorted((a, d))), tuple(sorted((c, b)))
        if e1 in Es or e2 in Es:
            continue
        Es -= {E[i], E[j]}
        Es |= {e1, e2}
        E[i], E[j] = e1, e2
    R = np.zeros_like(A)
    rng.shuffle(wts)
    for (a, b), w_ in zip(E, wts):
        R[a, b] = R[b, a] = w_
    return R


def modularity_q(C, n_mod=7):
    """Newman Q of a spectral split into n_mod communities (rough, for comparison only)."""
    k = C.sum(1)
    m2 = k.sum()
    B = C - np.outer(k, k) / m2
    vals, vecs = np.linalg.eigh(B)
    X = vecs[:, -n_mod:]
    # k-means on leading eigvecs
    rng = np.random.default_rng(0)
    cent = X[rng.choice(len(X), n_mod, replace=False)]
    for _ in range(50):
        lab = np.argmin(((X[:, None] - cent[None]) ** 2).sum(-1), 1)
        cent = np.array([X[lab == c].mean(0) if (lab == c).any() else cent[c] for c in range(n_mod)])
    same = lab[:, None] == lab[None]
    return float((B * same).sum() / m2)


def main():
    rng = np.random.default_rng(7)
    subj = {s: load(s) for s in SUBJECTS}
    w = np.mean([peak_freqs(tc) for _, tc in subj.values()], axis=0)
    out = {}

    # E1 + E2: G sweep on each subject
    Gs = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.3, 1.6, 2.0, 2.5, 3.0]
    fits = {g: [] for g in Gs}
    sims = {}
    for s, (C, tc) in subj.items():
        emp = fc(bandpass(tc))
        for g in Gs:
            x, env = simulate(C, w, g, np.random.default_rng(zlib.crc32(repr((s, g)).encode())))
            fits[g].append(np.corrcoef(emp, fc(bandpass(x)))[0, 1])
            sims[(s, g)] = env
    fit_mean = {g: float(np.mean(v)) for g, v in fits.items()}
    G_star = max(fit_mean, key=fit_mean.get)
    out["E1_fit"] = fit_mean
    out["G_star"] = G_star

    # threshold fixed on intact brain at G*
    thr = float(np.percentile(np.concatenate([drive(sims[(s, G_star)]) for s in SUBJECTS]), 95))
    out["threshold"] = thr

    e2 = {}
    for g in Gs:
        rates, cvs = zip(*[timing_stats(initiatives(drive(sims[(s, g)]), thr), sims[(s, g)].shape[1])
                           for s in SUBJECTS])
        e2[g] = {"rate_per_min": float(np.mean(rates)), "cv_isi": float(np.nanmean(cvs))}
    out["E2_rate_vs_G"] = e2

    # E3 do(Z) + E5 Granger + E4 rewire at G*
    conds = {
        "intact": {},
        "silence_DMN": {"silence": IDX["DMN"]},
        "silence_SEN": {"silence": IDX["SEN"]},
        "silence_VAL": {"silence": IDX["VAL"]},
        "stim_SEN": {"stim": IDX["SEN"], "stim_amp": 0.03},
    }
    e3 = {}
    for name, kw in conds.items():
        rates, cvs, gd, gs = [], [], [], []
        for s, (C, _) in subj.items():
            _, env = simulate(C, w, G_star, np.random.default_rng(zlib.crc32(repr((s, name)).encode())), **kw)
            D = drive(env)
            r, cv = timing_stats(initiatives(D, thr), env.shape[1])
            rates.append(r); cvs.append(cv)
            gd.append(granger(env[IDX["DMN"]].mean(0), D))
            gs.append(granger(env[IDX["SEN"]].mean(0), D))
        e3[name] = {"rate_per_min": float(np.mean(rates)), "cv_isi": float(np.nanmean(cvs)),
                    "GC_DMN_to_D": float(np.mean(gd)), "GC_SEN_to_D": float(np.mean(gs))}
    out["E3_E5_doZ"] = e3

    e4 = {}
    for label in ["intact", "rewired"]:
        rates, cvs, qs, fitv = [], [], [], []
        for s, (C, tc) in subj.items():
            Cx = C if label == "intact" else rewire(C, np.random.default_rng(int(s)))
            qs.append(modularity_q(Cx))
            x, env = simulate(Cx, w, G_star, np.random.default_rng(zlib.crc32(repr((s, label)).encode())))
            r, cv = timing_stats(initiatives(drive(env), thr), env.shape[1])
            rates.append(r); cvs.append(cv)
            fitv.append(np.corrcoef(fc(bandpass(tc)), fc(bandpass(x)))[0, 1])
        e4[label] = {"modularity_Q": float(np.mean(qs)), "rate_per_min": float(np.mean(rates)),
                     "cv_isi": float(np.nanmean(cvs)), "FC_fit": float(np.mean(fitv))}
    out["E4_topology"] = e4

    (HERE / "results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
