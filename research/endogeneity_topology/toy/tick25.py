"""Tick 25: does inhibition relax the self-boundary threshold mu_c?
SBM 10x100, mean degree 5. Conditions:
  exc        all links excitatory (tick 24 baseline)
  cross_inh  all between-module links inhibitory (lateral inhibition between motives)
  dale20     20% of nodes inhibitory (all their outgoing links negative)
Gain normalised on the excitatory part, rate-matched 0.03. Attribution (E) uses excitatory inputs only
(causes of firing); detector sees only positive lagged excess. 3 seeds."""
import io, contextlib, runpy
import numpy as np, networkx as nx, scipy.sparse as sps
from scipy.sparse.linalg import eigs
with contextlib.redirect_stdout(io.StringIO()):
    ns12 = runpy.run_path("tick12.py")
sim, E_of, infer, ari, N = ns12["sim"], ns12["E_of"], ns12["infer"], ns12["ari"], ns12["N"]

def sbm(seed, mu, size=100, deg=5.0):
    k = N//size; p_in = deg*(1-mu)/(size-1); p_out = deg*mu/(N-size)
    g = nx.stochastic_block_model([size]*k, [[p_in if i == j else p_out for j in range(k)] for i in range(k)], seed=seed, sparse=True)
    return nx.to_scipy_sparse_array(g, nodelist=range(N), format="csr", dtype=float), np.arange(N)//size

def signed(A, truth, cond, seed):
    A = A.tocoo(); w = np.ones_like(A.data)
    if cond == "cross_inh": w[truth[A.row] != truth[A.col]] = -1
    if cond == "dale20":
        inh = np.random.default_rng(seed+7).random(N) < 0.2; w[inh[A.col]] = -1     # col = presynaptic j
    S = sps.csr_matrix((w, (A.row, A.col)), shape=A.shape)
    Wp = S.maximum(0); lam = abs(eigs(Wp, k=1, which="LM", return_eigenvectors=False)[0])
    return S/lam, Wp/lam

mus, conds = [0.3, 0.2, 0.15, 0.1], ["exc", "cross_inh", "dale20"]
print(f"{'condition':<11}" + "".join(f"{'mu='+str(m):>13}" for m in mus) + "   (ARI / E gain / op gain)")
for cond in conds:
    cells = []
    for mu in mus:
        r = []
        for seed in [1, 2, 3]:
            A, truth = sbm(seed, mu); S1, P1 = signed(A, truth, cond, seed)
            lo, hi = 0.5, 3.0
            for _ in range(11):
                m_ = (lo+hi)/2; lo, hi = (m_, hi) if sim(S1*m_, seed, 1000)[500:].mean() < 0.03 else (lo, m_)
            gn = (lo+hi)/2; W, Wp = sps.csr_matrix(S1*gn), sps.csr_matrix(P1*gn)
            sp = sim(W, seed, 4500)[500:]; tr, tst = sp[:2000], sp[2000:]
            G = infer(tr); rng = np.random.default_rng(seed); best = None
            for res in [0.5, 1, 2, 4]:
                lab = np.empty(N, int)
                for k, c in enumerate(nx.community.louvain_communities(G, weight="weight", resolution=res, seed=seed)): lab[list(c)] = k
                ef, en = E_of(tst, Wp, lab), E_of(tst, Wp, lab[rng.permutation(N)])
                if best is None or ef-en > best[0]: best = (ef-en, lab)
            r.append((ari(best[1], truth), best[0], gn))
        m = np.mean(r, 0); cells.append(f"{m[0]:.2f}/{m[1]:.2f}/{m[2]:.2f}")
    print(f"{cond:<11}" + "".join(f"{c:>13}" for c in cells), flush=True)
