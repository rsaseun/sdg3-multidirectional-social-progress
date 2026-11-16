"""All computations for the paper.

Four modules answer the four research questions:

1. ``social_deprivation``  – country-level Alkire–Foster counting of social deprivations (RQ1)
2. ``directional_matrix``  – direction of association between each social dimension and each SDG 3 target (RQ2)
3. ``quantile_models``     – how strongly social deprivation relates to progress across the distribution (RQ3)
4. ``policy_leverage``     – gap-weighted, multi-target policy priorities and an SDG 1.2 halving scenario (RQ4)

``run_analysis`` runs everything and returns one results dictionary; ``save_results`` writes it to disk.
"""
import json
import warnings
from itertools import combinations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.regression.quantile_regression import QuantReg
from statsmodels.tools.sm_exceptions import IterationLimitWarning

from .config import (CUTOFF_SENS, DIMENSIONS, HALVING, K_GRID, K_MAIN, N_BOOT_CORR, N_BOOT_QR, Q_FDR, SEED,
                     SOCIAL, STABLE, TARGETS, TAUS)

warnings.simplefilter("ignore", IterationLimitWarning)
SOC = list(SOCIAL)
TGT = list(TARGETS)
FAMILY = {"Maternal, child and coverage targets": ["MMR", "SBA", "U5MR", "NMR", "FP", "ABR", "SCI", "DTP3"],
          "Infectious-disease targets": ["HIV", "TB"]}


# =================================================================================================================
# 0. Progress towards the SDG 3 targets
# =================================================================================================================
def attainment(d):
    """Target attainment on a 0–1 scale: 1 = SDR green threshold (target) met, 0 = at or beyond the SDR lower bound."""
    A, S = {}, {}
    for t, (_, _, sign, green, red, low) in TARGETS.items():
        x = d[t]
        a = (x - low) / (green - low) if sign > 0 else (low - x) / (low - green)
        A[t] = a.clip(0, 1)
        met = x >= green if sign > 0 else x <= green
        bad = x < red if sign > 0 else x > red
        S[t] = np.where(x.isna(), np.nan, np.where(met, 2, np.where(bad, 0, 1)))   # 2 achieved, 1 challenges, 0 red
    A = pd.DataFrame(A, index=d.index)
    S = pd.DataFrame(S, index=d.index)
    att = pd.DataFrame({"attainment": A.mean(axis=1) * 100,
                        "n_targets_met": (S == 2).sum(axis=1), "n_targets_red": (S == 0).sum(axis=1)})
    for fam, cols in FAMILY.items():
        att[fam] = A[cols].mean(axis=1) * 100
    return A, S, att


# =================================================================================================================
# 1. Alkire–Foster counting of social deprivations (RQ1)
# =================================================================================================================
def _weights(d):
    """Nested equal weights (dimension, then indicator), renormalised over each country's available indicators."""
    base = pd.Series({s: 1 / len(DIMENSIONS) / sum(SOCIAL[t][1] == SOCIAL[s][1] for t in SOC) for s in SOC})
    W = pd.DataFrame(np.tile(base.values, (len(d), 1)), index=d.index, columns=SOC).where(d[SOC].notna(), 0.0)
    return W.div(W.sum(axis=1), axis=0), base


def cutoffs(d, q=0.5):
    """Deprivation cutoffs: the q-th quantile counted from the advantaged end (q = 0.5: regional median)."""
    z = {}
    for s in SOC:
        worse = SOCIAL[s][2]
        z[s] = d[s].quantile(q) if worse > 0 else d[s].quantile(1 - q)
    return pd.Series(z)


def deprivation_matrix(d, z):
    """g0 (1 = deprived, strictly worse than the cutoff) and normalised gaps g1 in [0, 1]."""
    g0, g1 = {}, {}
    for s in SOC:
        x, worse = d[s], SOCIAL[s][2]
        if worse > 0:
            dep = x > z[s]
            gap = (x - z[s]) / (x.max() - z[s])
        else:
            dep = x < z[s]
            gap = (z[s] - x) / (z[s] - x.min())
        g0[s] = dep.astype(float).where(x.notna())
        g1[s] = gap.where(dep, 0.0).where(x.notna())
    return pd.DataFrame(g0), pd.DataFrame(g1)


def alkire_foster(d, q=0.5, k=K_MAIN, weights=None):
    """Return a dict with deprivation scores, identification and the H, A, M0, M1 measures."""
    W = _weights(d)[0] if weights is None else weights
    z = cutoffs(d, q)
    g0, g1 = deprivation_matrix(d, z)
    c = (g0.fillna(0) * W).sum(axis=1)
    iden = c >= k - 1e-9
    cens = (g0.fillna(0) * W).where(iden, 0.0, axis=0)
    H = iden.mean()
    A = c[iden].mean() if iden.any() else 0.0
    M0 = cens.sum(axis=1).mean()
    M1 = (g1.fillna(0) * W).where(iden, 0.0, axis=0).sum(axis=1).mean()
    dim_c = pd.DataFrame({D: cens[[s for s in SOC if SOCIAL[s][1] == D]].sum(axis=1) for D in DIMENSIONS})
    contrib = dim_c.mean() / M0 * 100 if M0 > 0 else dim_c.mean() * 0
    return dict(z=z, g0=g0, g1=g1, W=W, score=c, identified=iden, H=H, A=A, M0=M0, M1=M1,
                contrib=contrib, dim_censored=dim_c)


def dimension_deprivation(AF):
    """Dimension-level deprivation share (weighted share of the dimension's available indicators deprived)."""
    out = {}
    for D in DIMENSIONS:
        cols = [s for s in SOC if SOCIAL[s][1] == D]
        g = AF["g0"][cols]
        out[D] = g.mean(axis=1, skipna=True)
    return pd.DataFrame(out)


def codeprivation(AF):
    """Joint deprivation of dimension pairs relative to independence (lift > 1 = deprivations cluster)."""
    Dd = dimension_deprivation(AF) >= 0.5
    rows = []
    for a, b in combinations(DIMENSIONS, 2):
        m = Dd[[a, b]].notna().all(axis=1)
        pa, pb, pab = Dd.loc[m, a].mean(), Dd.loc[m, b].mean(), (Dd.loc[m, a] & Dd.loc[m, b]).mean()
        rows.append(dict(dim_a=a, dim_b=b, p_a=pa, p_b=pb, p_joint=pab, lift=pab / (pa * pb) if pa * pb > 0 else np.nan))
    n_dims = Dd.sum(axis=1)
    return pd.DataFrame(rows), n_dims


def social_deprivation(d, rng):
    """RQ1: main Alkire–Foster results, uncertainty, sensitivity and co-deprivation."""
    AF = alkire_foster(d)
    # bootstrap (countries) for M0, H and A at the main settings; cutoffs re-estimated in each resample
    boot = []
    for _ in range(N_BOOT_CORR):
        idx = rng.integers(0, len(d), len(d))
        db = d.iloc[idx].reset_index(drop=True)
        r = alkire_foster(db)
        boot.append((r["M0"], r["H"], r["A"]))
    boot = np.array(boot)
    ci = {m: np.percentile(boot[:, i], [2.5, 97.5]).tolist() for i, m in enumerate(["M0", "H", "A"])}
    # population-weighted headcount: share of the region's population living in identified countries
    pop = d["POP_M"]
    H_pop = pop[AF["identified"]].sum() / pop.sum()
    # sensitivity to the indicator cutoffs and to k
    sens = []
    for lab, q in CUTOFF_SENS.items():
        for k in K_GRID:
            r = alkire_foster(d, q=q, k=k)
            sens.append(dict(cutoff=lab, k=k, H=r["H"], A=r["A"], M0=r["M0"], M1=r["M1"]))
    sens = pd.DataFrame(sens)
    scores = pd.DataFrame({lab: alkire_foster(d, q=q)["score"] for lab, q in CUTOFF_SENS.items()})
    rank_agree = scores.corr(method="spearman")
    # equal indicator weights (instead of nested equal dimension weights)
    W_eq = pd.DataFrame(1.0, index=d.index, columns=SOC).where(d[SOC].notna(), 0.0)
    W_eq = W_eq.div(W_eq.sum(axis=1), axis=0)
    r_eq = alkire_foster(d, weights=W_eq)
    rank_agree_weights = stats.spearmanr(AF["score"], r_eq["score"])[0]
    co, n_dims = codeprivation(AF)
    country = pd.DataFrame({"deprivation_score": AF["score"], "identified": AF["identified"],
                            "n_dimensions_deprived": n_dims,
                            "n_indicators_available": d[SOC].notna().sum(axis=1)})
    country = country.join(AF["dim_censored"].add_prefix("censored_"))
    return dict(AF=AF, ci=ci, H_pop=H_pop, sensitivity=sens, rank_agree=rank_agree,
                rank_agree_weights=rank_agree_weights, codeprivation=co, country=country,
                dim_share=dimension_deprivation(AF), M0_equal_weights=r_eq["M0"])


# =================================================================================================================
# 2. Directional association matrix (RQ2)
# =================================================================================================================
def _rank_rows(X):
    return stats.rankdata(X, axis=-1)


def _partial_r(x, y, z):
    """Partial Spearman correlation of x and y given z (one or more controls), vectorised over rows.

    x, y: (B, n); z: (B, n) or (B, n, p). Ranks of x and y are residualised on the ranks of every control.
    """
    rx, ry = _rank_rows(x), _rank_rows(y)
    z = z[..., None] if z.ndim == 2 else z
    rz = np.stack([_rank_rows(z[..., j]) for j in range(z.shape[-1])], axis=-1)
    Zc = np.concatenate([np.ones(rz.shape[:-1] + (1,)), rz], axis=-1)            # (B, n, p+1)
    G = np.einsum("bni,bnj->bij", Zc, Zc)

    def resid(a):
        beta = np.linalg.solve(G, np.einsum("bni,bn->bi", Zc, a)[..., None])[..., 0]
        return a - np.einsum("bni,bi->bn", Zc, beta)
    ex, ey = resid(rx), resid(ry)
    num = (ex * ey).sum(axis=-1)
    den = np.sqrt((ex ** 2).sum(axis=-1) * (ey ** 2).sum(axis=-1))
    return num / den


def _spearman_rows(x, y):
    rx, ry = _rank_rows(x), _rank_rows(y)
    rx = rx - rx.mean(axis=-1, keepdims=True)
    ry = ry - ry.mean(axis=-1, keepdims=True)
    return (rx * ry).sum(axis=-1) / np.sqrt((rx ** 2).sum(axis=-1) * (ry ** 2).sum(axis=-1))


def bh(p):
    """Benjamini–Hochberg adjusted p-values."""
    p = np.asarray(p, float)
    o = np.argsort(p)
    q = p[o] * len(p) / np.arange(1, len(p) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty_like(q)
    out[o] = np.minimum(q, 1)
    return out


def advantage(d):
    """Social indicators re-oriented so that higher = socially advantaged."""
    return pd.DataFrame({s: -SOCIAL[s][2] * d[s] for s in SOC}, index=d.index)


def dimension_advantage(d):
    """Dimension advantage score: mean of the standardised advantage indicators in each dimension."""
    adv = advantage(d)
    zs = (adv - adv.mean()) / adv.std()
    return pd.DataFrame({D: zs[[s for s in SOC if SOCIAL[s][1] == D]].mean(axis=1) for D in DIMENSIONS})


def assoc_matrix(X, A, Z, rng, n_boot=N_BOOT_CORR, adjust=True):
    """Partial (or simple) Spearman correlations of each column of X with each column of A, with bootstrap sign
    stability, t-test p-values and Benjamini–Hochberg q-values. Returns a long DataFrame."""
    rows = []
    for s in X.columns:
        for t in A.columns:
            Zf = Z.to_frame() if isinstance(Z, pd.Series) else Z
            m = X[s].notna() & A[t].notna() & (Zf.notna().all(axis=1) if adjust else True)
            x, y, z = X.loc[m, s].values, A.loc[m, t].values, Zf[m].values
            n = len(x)
            r = float(_partial_r(x[None], y[None], z[None])[0] if adjust else _spearman_rows(x[None], y[None])[0])
            df = n - 2 - Zf.shape[1] if adjust else n - 2
            tval = r * np.sqrt(df / max(1 - r * r, 1e-12))
            p = 2 * stats.t.sf(abs(tval), df)
            idx = rng.integers(0, n, (n_boot, n))
            rb = _partial_r(x[idx], y[idx], z[idx]) if adjust else _spearman_rows(x[idx], y[idx])
            rb = rb[np.isfinite(rb)]
            stab = float(np.mean(np.sign(rb) == np.sign(r)))
            lo, hi = np.percentile(rb, [2.5, 97.5])
            rows.append(dict(social=s, target=t, n=n, r=r, ci_low=lo, ci_high=hi, p=p, sign_stability=stab))
    L = pd.DataFrame(rows)
    L["q"] = bh(L["p"])
    L["direction"] = np.where((L["q"] < Q_FDR) & (L["sign_stability"] >= STABLE),
                              np.where(L["r"] > 0, "convergent", "divergent"), "undetermined")
    return L


def directional_matrix(d, A, rng):
    """RQ2: indicator- and dimension-level direction matrices with sensitivity analyses."""
    adv = advantage(d)
    main = assoc_matrix(adv, A, d["lnGDP"], rng)
    dim = assoc_matrix(dimension_advantage(d), A, d["lnGDP"], rng)
    sens = {}
    sens["unadjusted"] = assoc_matrix(adv, A, d["lnGDP"], rng, adjust=False)
    keep = d["HIV"].rank(ascending=False) > 10          # drop the ten countries with the highest HIV incidence
    sens["excluding high-HIV decile"] = assoc_matrix(adv[keep], A[keep], d.loc[keep, "lnGDP"], rng)
    sens["adjusted for income and urbanisation"] = assoc_matrix(adv, A, d[["lnGDP", "URBAN"]], rng)
    agree = {}
    for k, S in sens.items():
        mm = main.merge(S[["social", "target", "r", "direction"]], on=["social", "target"], suffixes=("", "_s"))
        cls = mm[mm["direction"] != "undetermined"]
        agree[k] = dict(sign_agreement=float(np.mean(np.sign(mm["r"]) == np.sign(mm["r_s"]))),
                        classified_retained=float(np.mean(cls["direction"] == cls["direction_s"])) if len(cls) else np.nan,
                        n_convergent=int((S["direction"] == "convergent").sum()),
                        n_divergent=int((S["direction"] == "divergent").sum()))
    summ = main.groupby("social").agg(n_convergent=("direction", lambda x: int((x == "convergent").sum())),
                                      n_divergent=("direction", lambda x: int((x == "divergent").sum())),
                                      mean_r=("r", "mean")).reindex(SOC)
    summ["net_leverage"] = summ["n_convergent"] - summ["n_divergent"]
    summ["profile"] = np.select([(summ.n_convergent > 0) & (summ.n_divergent > 0), summ.n_convergent > 0,
                                 summ.n_divergent > 0], ["multi-directed", "convergent", "divergent"], "undetermined")
    return dict(matrix=main, dim_matrix=dim, sensitivity=sens, agreement=agree, summary=summ)


# =================================================================================================================
# 3. Quantile regression (RQ3)
# =================================================================================================================
def _qr_fit(y, X, tau):
    return QuantReg(y, X).fit(q=tau, max_iter=5000).params


def qr_profile(y, x, z, rng, n_boot=N_BOOT_QR, taus=TAUS):
    """Quantile regressions of y on x (social deprivation) controlling for z (centred), with bootstrap intervals."""
    m = y.notna() & x.notna() & z.notna()
    y, x, z = y[m].values, x[m].values, z[m].values
    X = np.column_stack([np.ones(len(y)), x, z - z.mean()])
    est = np.array([_qr_fit(y, X, t) for t in taus])
    B = np.empty((n_boot, len(taus), 3))
    for b in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        for j, t in enumerate(taus):
            B[b, j] = _qr_fit(y[i], X[i], t)
    ols = sm.OLS(y, X).fit(cov_type="HC3")
    out = pd.DataFrame({"tau": taus, "beta": est[:, 1], "ci_low": np.percentile(B[:, :, 1], 2.5, axis=0),
                        "ci_high": np.percentile(B[:, :, 1], 97.5, axis=0), "intercept": est[:, 0],
                        "beta_lnGDP": est[:, 2]})
    lo, hi = (taus.index(0.2), taus.index(0.8)) if 0.2 in taus else (0, len(taus) - 1)
    diff = B[:, lo, 1] - B[:, hi, 1]
    test = dict(taus=[taus[lo], taus[hi]], diff_20_80=float(est[lo, 1] - est[hi, 1]), ci=np.percentile(diff, [2.5, 97.5]).tolist(),
                share_steeper_at_20=float(np.mean(diff < 0)))
    return dict(table=out, ols=dict(beta=float(ols.params[1]), ci=ols.conf_int()[1].tolist(), p=float(ols.pvalues[1]),
                                    r2=float(ols.rsquared)), test=test, n=int(m.sum()), zmean=float(z.mean()))


def quantile_models(d, att, AF, rng):
    """RQ3: main model on mean attainment, target families and dimension-specific models."""
    x = AF["score"] * 100      # deprivation score in percentage points of weighted indicators
    main = qr_profile(att["attainment"], x, d["lnGDP"], rng)
    fam = {f: qr_profile(att[f], x, d["lnGDP"], rng, n_boot=N_BOOT_QR // 2) for f in FAMILY}
    dimdis = -dimension_advantage(d)       # higher = more disadvantaged (SD units)
    dims = {}
    for D in DIMENSIONS:
        r = qr_profile(att["attainment"], dimdis[D], d["lnGDP"], rng, n_boot=N_BOOT_QR // 2, taus=[0.25, 0.5, 0.75])
        dims[D] = r
    return dict(main=main, families=fam, dimensions=dims, x=x)


# =================================================================================================================
# 4. Policy leverage and the SDG 1.2 halving scenario (RQ4)
# =================================================================================================================
def country_quantile(y, x, z, qr_table, zmean):
    """Conditional-quantile position of each country: where its observed value falls among the fitted quantiles."""
    taus = qr_table["tau"].values
    fitted = np.array([r.intercept + r.beta * x + r.beta_lnGDP * (z - zmean) for r in qr_table.itertuples()])
    fitted = np.maximum.accumulate(fitted, axis=0)        # enforce monotone quantile curves (rearrangement)
    pos = np.array([np.interp(y[i], fitted[:, i], taus) if np.isfinite(y[i]) else np.nan for i in range(len(y))])
    return np.clip(pos, taus.min(), taus.max())


def policy_leverage(d, A, AF, DM, QM):
    """RQ4: gap-weighted leverage of each social dimension in each country, priorities and the halving scenario."""
    M = DM["dim_matrix"].pivot(index="social", columns="target", values="r").reindex(index=DIMENSIONS, columns=TGT)
    C = DM["dim_matrix"].pivot(index="social", columns="target", values="direction").reindex(index=DIMENSIONS, columns=TGT)
    Wt = M.where(C == "convergent", 0.0) - M.abs().where(C == "divergent", 0.0)
    need = 1 - A[TGT]
    gap = pd.DataFrame({D: AF["g1"][[s for s in SOC if SOCIAL[s][1] == D]].mean(axis=1) for D in DIMENSIONS}).fillna(0)
    lev = pd.DataFrame({D: gap[D] * need.fillna(0).values.dot(Wt.loc[D].values) for D in DIMENSIONS}, index=d.index)
    lev = lev.clip(lower=0)
    share = lev.div(lev.sum(axis=1).replace(0, np.nan), axis=0) * 100
    order = lev.apply(lambda r: list(r.sort_values(ascending=False).index[r.sort_values(ascending=False) > 0]), axis=1)
    pri = pd.DataFrame({"priority_1": order.map(lambda o: o[0] if len(o) else "No gap below the regional median"),
                        "priority_2": order.map(lambda o: o[1] if len(o) > 1 else "")}, index=d.index)
    # halving scenario with quantile-specific slopes
    main = QM["main"]
    y = (A[TGT].mean(axis=1) * 100).values
    x = QM["x"].values
    tau_c = country_quantile(y, x, d["lnGDP"].values, main["table"], main["zmean"])
    beta_c = np.interp(tau_c, main["table"]["tau"], main["table"]["beta"])
    dx = HALVING * x
    scen = pd.DataFrame({"attainment": y, "deprivation_score": x, "tau_position": tau_c, "beta_tau": beta_c,
                         "gain_quantile": -beta_c * dx, "gain_ols": -main["ols"]["beta"] * dx}, index=d.index)
    scen["attainment_scenario"] = (scen["attainment"] + scen["gain_quantile"]).clip(upper=100)
    pop = d["POP_M"]
    sm_ = dict(mean_gain_quantile=float(scen.gain_quantile.mean()), mean_gain_ols=float(scen.gain_ols.mean()),
               popw_gain_quantile=float(np.average(scen.gain_quantile, weights=pop)),
               popw_gain_ols=float(np.average(scen.gain_ols, weights=pop)),
               corr_gain_attainment=float(stats.spearmanr(scen.gain_quantile, scen.attainment)[0]),
               gain_bottom_third=float(scen.loc[scen.attainment <= scen.attainment.quantile(1 / 3), "gain_quantile"].mean()),
               gain_top_third=float(scen.loc[scen.attainment >= scen.attainment.quantile(2 / 3), "gain_quantile"].mean()),
               gain_ols_bottom_third=float(scen.loc[scen.attainment <= scen.attainment.quantile(1 / 3), "gain_ols"].mean()),
               gain_ols_top_third=float(scen.loc[scen.attainment >= scen.attainment.quantile(2 / 3), "gain_ols"].mean()),
               n_reaching_75=int(((scen.attainment < 75) & (scen.attainment_scenario >= 75)).sum()),
               n_above_75_now=int((scen.attainment >= 75).sum()))
    # robustness of first priorities: weight every target by the signed dimension correlation, classified or not
    lev_alt = pd.DataFrame({D: gap[D] * need.fillna(0).values.dot(M.loc[D].fillna(0).values) for D in DIMENSIONS},
                           index=d.index).clip(lower=0)
    has = lev.sum(axis=1) > 0
    alt1 = lev_alt.idxmax(axis=1).where(lev_alt.sum(axis=1) > 0, "No gap below the regional median")
    sm_["priority_agreement_alt_weights"] = float((alt1[has] == pri.loc[has, "priority_1"]).mean())
    sm_["priority_in_top2_alt_weights"] = float(np.mean([pri.loc[c, "priority_1"] in
                                                         list(lev_alt.loc[c].sort_values(ascending=False).index[:2])
                                                         for c in d.index[has]]))
    counts = pri["priority_1"].value_counts()
    return dict(weights=Wt, gap=gap, leverage=lev, share=share, priorities=pri, scenario=scen, scenario_summary=sm_,
                priority_counts=counts)


# =================================================================================================================
# Orchestration
# =================================================================================================================
def run_analysis(d, geo=None):
    """Run the four modules and return the results dictionary used by the figure and table scripts."""
    rng = np.random.default_rng(SEED)
    A, S, att = attainment(d)
    SD = social_deprivation(d, rng)
    DM = directional_matrix(d, A, rng)
    QM = quantile_models(d, att, SD["AF"], rng)
    PL = policy_leverage(d, A, SD["AF"], DM, QM)
    R = dict(d=d, geo=geo, A=A, status=S, att=att, SD=SD, DM=DM, QM=QM, PL=PL)
    R["headline"] = headline(R)
    return R


def headline(R):
    d, SD, DM, QM, PL, att, S = R["d"], R["SD"], R["DM"], R["QM"], R["PL"], R["att"], R["status"]
    AF = SD["AF"]
    mx = DM["matrix"]
    co = SD["codeprivation"]
    q = QM["main"]["table"].set_index("tau")
    h = dict(
        n_countries=len(d), targets_met_total=int((S == 2).sum().sum()), targets_assessed=int(S.notna().sum().sum()),
        countries_meeting_none=int(((S == 2).sum(axis=1) == 0).sum()),
        share_red=float((S == 0).sum().sum() / S.notna().sum().sum()),
        attainment_mean=float(att.attainment.mean()), attainment_min=float(att.attainment.min()),
        attainment_max=float(att.attainment.max()),
        H=float(AF["H"]), A=float(AF["A"]), M0=float(AF["M0"]), M1=float(AF["M1"]), ci=SD["ci"], H_pop=float(SD["H_pop"]),
        n_identified=int(AF["identified"].sum()), contrib={k: float(v) for k, v in AF["contrib"].items()},
        rank_agree_min=float(SD["rank_agree"].values[np.triu_indices(3, 1)].min()),
        rank_agree_weights=float(SD["rank_agree_weights"]),
        lift_max=co.loc[co.lift.idxmax(), ["dim_a", "dim_b", "lift", "p_joint"]].to_dict(),
        lift_mean=float(co.lift.mean()), n_lift_above1=int((co.lift > 1).sum()), n_pairs=len(co),
        n_pairs_assoc=len(mx), n_convergent=int((mx.direction == "convergent").sum()),
        n_divergent=int((mx.direction == "divergent").sum()),
        multi_directed=[s for s, r in DM["summary"].iterrows() if r.profile == "multi-directed"],
        agreement=DM["agreement"],
        qr_beta={str(t): float(q.loc[t, "beta"]) for t in q.index}, qr_ci={str(t): [float(q.loc[t, "ci_low"]),
                                                                              float(q.loc[t, "ci_high"])] for t in q.index},
        qr_ols=QM["main"]["ols"], qr_test=QM["main"]["test"], qr_n=QM["main"]["n"],
        families={f: dict(beta20=float(r["table"].set_index("tau").loc[0.2, "beta"]),
                          beta50=float(r["table"].set_index("tau").loc[0.5, "beta"]),
                          beta80=float(r["table"].set_index("tau").loc[0.8, "beta"]), ols=r["ols"], test=r["test"])
                  for f, r in QM["families"].items()},
        priority_counts={k: int(v) for k, v in PL["priority_counts"].items()},
        scenario=PL["scenario_summary"],
    )
    return h


def _json(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def save_results(R, out_dir):
    """Write all numerical results to out_dir/results (CSV and JSON)."""
    o = out_dir / "results"
    o.mkdir(parents=True, exist_ok=True)
    R["A"].to_csv(o / "target_attainment.csv")
    R["status"].to_csv(o / "target_status.csv")
    R["att"].to_csv(o / "attainment_summary.csv")
    SD = R["SD"]
    SD["country"].to_csv(o / "af_country.csv")
    SD["AF"]["g0"].to_csv(o / "af_deprivation_matrix.csv")
    SD["AF"]["z"].rename("cutoff").to_csv(o / "af_cutoffs.csv")
    SD["sensitivity"].to_csv(o / "af_sensitivity.csv", index=False)
    SD["codeprivation"].to_csv(o / "af_codeprivation.csv", index=False)
    SD["rank_agree"].to_csv(o / "af_rank_agreement.csv")
    DM = R["DM"]
    DM["matrix"].to_csv(o / "direction_matrix.csv", index=False)
    DM["dim_matrix"].to_csv(o / "direction_matrix_dimensions.csv", index=False)
    DM["summary"].to_csv(o / "direction_summary.csv")
    for k, S in DM["sensitivity"].items():
        S.to_csv(o / f"direction_matrix_sens_{k.replace(' ', '_')}.csv", index=False)
    QM = R["QM"]
    QM["main"]["table"].to_csv(o / "qr_main.csv", index=False)
    for f, r in QM["families"].items():
        r["table"].to_csv(o / f"qr_family_{f.split()[0].lower().strip(',')}.csv", index=False)
    pd.concat({D: r["table"] for D, r in QM["dimensions"].items()}, names=["dimension"]).to_csv(o / "qr_dimensions.csv")
    PL = R["PL"]
    PL["leverage"].to_csv(o / "policy_leverage.csv")
    PL["priorities"].to_csv(o / "policy_priorities.csv")
    PL["scenario"].to_csv(o / "halving_scenario.csv")
    with open(o / "headline.json", "w") as f:
        json.dump(R["headline"], f, indent=1, default=_json)
