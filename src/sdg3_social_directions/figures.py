"""One function per figure. Each takes the results dictionary R and an output path stem."""
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch, Rectangle

from .analysis import FAMILY, SOC
from .config import (COL, DIM_COL, DIM_HATCH, DIM_SHORT, DIMENSIONS, K_MAIN, MM, SOC_SHORT, SOCIAL, TARGETS,
                     save_figure, set_style)

plt = set_style()
SHORT_TGT = {t: f"{v[0]}\n({v[1]})" for t, v in TARGETS.items()}
SHORT_TGT.update({"FP": "Family planning\n(3.7.1)", "SCI": "UHC coverage\n(3.8.1)", "SBA": "Skilled birth\nattendance (3.1.2)",
                  "TB": "Tuberculosis\n(3.3.2)", "HIV": "HIV incidence\n(3.3.1)", "DTP3": "DTP3\n(3.b.1)",
                  "ABR": "Adolescent\nbirths (3.7.2)", "MMR": "Maternal\nmortality (3.1.1)", "U5MR": "Under-five\nmortality (3.2.1)",
                  "NMR": "Neonatal\nmortality (3.2.2)"})
TGT_ORDER = FAMILY["Maternal, child and coverage targets"] + FAMILY["Infectious-disease targets"]
SOC_ORDER = [s for D in DIMENSIONS for s in SOC if SOCIAL[s][1] == D]
NAME = {"Central African Republic": "Central African Rep.", "Congo, Dem. Rep.": "DR Congo", "Congo, Rep.": "Congo",
        "São Tomé and Príncipe": "São Tomé & Príncipe", "Gambia, The": "The Gambia"}


def _nm(c):
    return NAME.get(c, c)


def _panel(ax, letter, x=-0.02, y=1.02):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom", ha="right")


def _map(R, ax, values, cmap=None, norm=None, categorical=None, edge="white"):
    ssa, ctx = R["geo"]
    ctx.plot(ax=ax, color="#EEEEEE", edgecolor="white", linewidth=0.3)
    g = ssa.merge(values.rename("v"), left_on="country", right_index=True, how="left")
    if categorical is None:
        g.plot(ax=ax, column="v", cmap=cmap, norm=norm, edgecolor=edge, linewidth=0.3,
               missing_kwds=dict(color="white", hatch="////", edgecolor="0.6", linewidth=0.3))
    else:
        for cat, (col, hatch) in categorical.items():
            sub = g[g["v"] == cat]
            if len(sub):
                sub.plot(ax=ax, color=col, edgecolor="0.25", linewidth=0.3, hatch=hatch)
    ax.set_xlim(-26, 58)
    ax.set_ylim(-36, 28)
    ax.set_axis_off()
    return g


# ---------------------------------------------------------------------------------------------------------------
def figure_1_framework(R, path):
    """Conceptual framework: four directions of social progress towards the SDG 3 targets."""
    fig, ax = plt.subplots(figsize=(174 * MM, 100 * MM))
    ax.set_xlim(0, 100)
    ax.set_ylim(-6, 58)
    ax.set_axis_off()

    def box(x, y, w, h, title, text, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.0", fc=fc, ec="0.3", lw=0.7))
        ax.text(x + w / 2, y + h - 1.6, title, ha="center", va="top", fontsize=6.8, fontweight="bold")
        ax.text(x + w / 2, y + h - 5.0, text, ha="center", va="top", fontsize=6.0, linespacing=1.25)

    def arrow(p, q, color="0.3", ls="-"):
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=8, color=color, lw=0.9, linestyle=ls))
    ax.text(9, 56, "Social dimensions", ha="center", fontsize=7, fontweight="bold")
    for i, D in enumerate(DIMENSIONS):
        y = 47 - i * 8.2
        ax.add_patch(Rectangle((0.5, y), 17, 6, fc=DIM_COL[D], ec="0.25", lw=0.5, hatch=DIM_HATCH[D], alpha=0.35))
        ax.text(9, y + 3, D.replace(" and ", "\nand "), ha="center", va="center", fontsize=6, linespacing=1.1,
                bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.6))
    box(21.5, 37, 20, 16, "RQ1  Dimensions", "Alkire–Foster counting\nof social deprivations:\nhow they combine\nand compound", "#F2F2F2")
    box(46, 37, 21, 16, "RQ2  Direction", "convergent (+) and\ndivergent (−) links with\nten SDG 3 targets,\nnet of national income", "#F2F2F2")
    box(46, 15.5, 21, 16, "RQ3  Distribution", "quantile regression:\nis social deprivation more\nconsequential for laggards\nthan for leaders?", "#F2F2F2")
    box(21.5, 0, 45.5, 10.5, "RQ4  Policy", "gap-weighted multi-target leverage → country entry points;\nSDG 1.2-style halving of deprivation → attainment gains by 2030",
        "#E8F1F8")
    ax.text(86, 56, "SDG 3 targets", ha="center", fontsize=7, fontweight="bold")
    for i, t in enumerate(TGT_ORDER):
        y = 50.4 - i * 5.15
        mcc = t in FAMILY["Maternal, child and coverage targets"]
        ax.add_patch(Rectangle((73, y), 26, 4.1, fc="#DCEBF5" if mcc else "#FBE3D3", ec="0.4", lw=0.5,
                               hatch="" if mcc else "....."))
        ax.text(74, y + 2.05, f"{TARGETS[t][1]}  {TARGETS[t][0].replace(' (modern methods)', '')}", ha="left", va="center", fontsize=5.8,
                bbox=None if mcc else dict(fc="#FBE3D3", ec="none", pad=0.3))
    arrow((17.8, 30), (21.8, 42))
    arrow((41.4, 45), (45.6, 45))
    arrow((67.4, 48), (72.6, 40), color=COL["convergent"])
    arrow((67.4, 42), (72.6, 6), color=COL["divergent"], ls="--")
    ax.text(70.6, 46, "+", color=COL["convergent"], fontsize=10, fontweight="bold", ha="center")
    ax.text(68.6, 26, "−", color=COL["divergent"], fontsize=10, fontweight="bold", ha="center")
    arrow((56.5, 36.6), (56.5, 31.9))
    arrow((56.5, 15.1), (56.5, 10.9))
    arrow((31.5, 36.6), (31.5, 10.9))
    ax.legend(handles=[Patch(fc="#DCEBF5", ec="0.4", label="Maternal, child and coverage targets"),
                       Patch(fc="#FBE3D3", ec="0.4", hatch=".....", label="Infectious-disease targets"),
                       Line2D([], [], color=COL["convergent"], label="Convergent direction"),
                       Line2D([], [], color=COL["divergent"], ls="--", label="Divergent direction")],
              loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=4, frameon=False, fontsize=6)
    save_figure(fig, path)


# ---------------------------------------------------------------------------------------------------------------
def figure_2_deprivation_profiles(R, path):
    """Country deprivation profiles (Alkire–Foster g0 matrix) and weighted deprivation scores."""
    AF = R["SD"]["AF"]
    sc = AF["score"].sort_values()
    g0 = AF["g0"].loc[sc.index, SOC_ORDER]
    fig = plt.figure(figsize=(174 * MM, 205 * MM))
    gs = fig.add_gridspec(1, 2, width_ratios=[3.2, 1.25], wspace=0.04)
    ax = fig.add_subplot(gs[0])
    axb = fig.add_subplot(gs[1], sharey=ax)
    n, m = g0.shape
    for i, c in enumerate(g0.index):
        for j, s in enumerate(g0.columns):
            v = g0.loc[c, s]
            D = SOCIAL[s][1]
            if np.isnan(v):
                ax.add_patch(Rectangle((j, i), 1, 1, fc="white", ec="0.75", lw=0.3, hatch="xxxx"))
            elif v == 1:
                ax.add_patch(Rectangle((j, i), 1, 1, fc=DIM_COL[D], ec="white", lw=0.4))
            else:
                ax.add_patch(Rectangle((j, i), 1, 1, fc="#F3F3F3", ec="white", lw=0.4))
    ax.set_xlim(0, m)
    ax.set_ylim(0, n)
    ax.set_yticks(np.arange(n) + 0.5)
    ax.set_yticklabels([_nm(c) for c in g0.index], fontsize=6)
    ax.set_xticks(np.arange(m) + 0.5)
    ax.set_xticklabels([SOC_SHORT[s] for s in g0.columns], rotation=90, fontsize=6.5, linespacing=1.0)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    # dimension brackets on top
    start = 0
    for D in DIMENSIONS:
        k = sum(SOCIAL[s][1] == D for s in SOC)
        ax.plot([start + 0.1, start + k - 0.1], [n + 0.5] * 2, color=DIM_COL[D], lw=2.2, clip_on=False)
        ax.text(start + k / 2, n + 1.0, DIM_SHORT[D], ha="center", va="bottom", fontsize=6.5)
        start += k
    iden = AF["identified"].loc[sc.index]
    axb.barh(np.arange(n) + 0.5, sc.values * 100, height=0.72,
             color=np.where(iden, "#555555", "#BBBBBB"), edgecolor="none")
    axb.axvline(K_MAIN * 100, color="black", lw=0.8, ls="--")
    axb.text(K_MAIN * 100, n + 0.4, "k = 1/3", fontsize=6.5, ha="center", va="bottom")
    axb.set_xlim(0, 100)
    axb.set_xlabel("Weighted deprivation score (%)")
    axb.tick_params(axis="y", left=False, labelleft=False)
    for sp in ("top", "right"):
        axb.spines[sp].set_visible(False)
    _panel(ax, "a", x=-0.01, y=1.035)
    _panel(axb, "b", x=-0.02, y=1.035)
    handles = [Patch(fc="#F3F3F3", label="Not deprived"), Patch(fc="white", ec="0.6", hatch="xxxx", label="Missing"),
               Patch(fc="#555555", label="Identified as socially deprived (score ≥ k)"),
               Patch(fc="#BBBBBB", label="Below k")]
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.0))
    save_figure(fig, path)


# ---------------------------------------------------------------------------------------------------------------
def figure_3_geography_compounding(R, path):
    """(a) Map of deprivation scores; (b) dimensional contributions to M0; (c) co-deprivation lift."""
    SD = R["SD"]
    AF = SD["AF"]
    fig = plt.figure(figsize=(174 * MM, 100 * MM))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.35, 1], height_ratios=[1, 1.15], wspace=0.25, hspace=0.55)
    ax = fig.add_subplot(gs[:, 0])
    cmap = plt.get_cmap("YlOrBr")
    _map(R, ax, AF["score"] * 100, cmap=cmap, norm=plt.Normalize(0, 100))
    sm_ = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 100))
    cb = fig.colorbar(sm_, ax=ax, orientation="horizontal", fraction=0.04, pad=0.02, shrink=0.7)
    cb.set_label("Weighted social deprivation score (%)")
    cb.ax.axvline(K_MAIN * 100, color="black", lw=1)
    _panel(ax, "a", x=0.02, y=0.98)
    axc = fig.add_subplot(gs[0, 1])
    ct = AF["contrib"].reindex(DIMENSIONS)
    y = np.arange(len(ct))
    for i, D in enumerate(DIMENSIONS):
        axc.barh(i, ct[D], color=DIM_COL[D], hatch=DIM_HATCH[D], edgecolor="0.25", lw=0.4)
        axc.text(24.8, i, f"{ct[D]:.1f}", va="center", ha="right", fontsize=6.5)
    axc.set_yticks(y)
    axc.set_yticklabels([DIM_SHORT[D] for D in DIMENSIONS])
    axc.invert_yaxis()
    axc.set_xlabel("Contribution to adjusted headcount ratio M0 (%)")
    axc.axvline(100 / 6, color="0.4", lw=0.6, ls=":")
    axc.set_xlim(0, 25)
    axc.set_xticks([0, 5, 10, 15, 20])
    for sp in ("top", "right"):
        axc.spines[sp].set_visible(False)
    _panel(axc, "b", x=-0.25)
    axl = fig.add_subplot(gs[1, 1])
    co = SD["codeprivation"]
    Lm = pd.DataFrame(np.nan, index=DIMENSIONS, columns=DIMENSIONS)
    for r in co.itertuples():
        Lm.loc[r.dim_b, r.dim_a] = r.lift
    norm = TwoSlopeNorm(vmin=0.5, vcenter=1, vmax=1.5)
    im = axl.imshow(Lm.values, cmap="PuOr_r", norm=norm)
    for i in range(6):
        for j in range(6):
            if np.isfinite(Lm.values[i, j]):
                axl.text(j, i, f"{Lm.values[i, j]:.2f}", ha="center", va="center", fontsize=6,
                         color="white" if abs(Lm.values[i, j] - 1) > 0.3 else "black")
    axl.set_xticks(range(6))
    axl.set_xticklabels([DIM_SHORT[D] for D in DIMENSIONS], rotation=40, ha="right", fontsize=6.5)
    axl.set_yticks(range(6))
    axl.set_yticklabels([DIM_SHORT[D] for D in DIMENSIONS], fontsize=6.5)
    axl.set_xlim(-0.5, 4.5)
    axl.set_ylim(5.5, 0.5)
    for sp in axl.spines.values():
        sp.set_visible(False)
    cb2 = fig.colorbar(im, ax=axl, fraction=0.05, pad=0.03)
    cb2.set_label("Co-deprivation lift", fontsize=6.5)
    cb2.ax.tick_params(labelsize=6)
    _panel(axl, "c", x=-0.25)
    save_figure(fig, path)


# ---------------------------------------------------------------------------------------------------------------
def figure_4_direction_matrix(R, path):
    """Directional association matrix: partial Spearman correlations (net of log GDP per capita)."""
    mx = R["DM"]["matrix"]
    Rm = mx.pivot(index="social", columns="target", values="r").reindex(index=SOC_ORDER, columns=TGT_ORDER)
    Cm = mx.pivot(index="social", columns="target", values="direction").reindex(index=SOC_ORDER, columns=TGT_ORDER)
    fig = plt.figure(figsize=(174 * MM, 118 * MM))
    gs = fig.add_gridspec(1, 2, width_ratios=[10, 2.2], wspace=0.05)
    ax = fig.add_subplot(gs[0])
    norm = TwoSlopeNorm(vmin=-0.7, vcenter=0, vmax=0.7)
    cmap = plt.get_cmap("RdBu")          # blue = convergent (positive), red = divergent (negative)
    im = ax.imshow(Rm.values, cmap=cmap, norm=norm, aspect="auto")
    for i in range(Rm.shape[0]):
        for j in range(Rm.shape[1]):
            r, c = Rm.values[i, j], Cm.values[i, j]
            txt = f"{r:.2f}"
            if c == "convergent":
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec="black", lw=1.1))
                txt += "\n+"
            elif c == "divergent":
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec="black", lw=1.1, ls="--"))
                txt += "\n−"
            ax.text(j, i, txt, ha="center", va="center", fontsize=5.6, color="white" if abs(r) > 0.45 else "black",
                    linespacing=0.9)
    ax.set_xticks(range(len(TGT_ORDER)))
    ax.set_xticklabels([f"{TARGETS[t][0].replace(' (modern methods)', '')} ({TARGETS[t][1]})" for t in TGT_ORDER],
                       fontsize=6.3, rotation=35, ha="left", rotation_mode="anchor")
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(SOC_ORDER)))
    ax.set_yticklabels([SOCIAL[s][0] for s in SOC_ORDER], fontsize=6.5)
    ax.tick_params(length=0)
    ax.axvline(len(FAMILY["Maternal, child and coverage targets"]) - 0.5, color="black", lw=1.2)
    start, dim_pos = -0.5, []
    for D in DIMENSIONS:
        k = sum(SOCIAL[s][1] == D for s in SOC)
        ax.axhline(start, color="white", lw=2)
        dim_pos.append((D, start + k / 2))
        start += k
    for sp in ax.spines.values():
        sp.set_visible(False)
    cb = fig.colorbar(im, ax=ax, orientation="horizontal", fraction=0.035, pad=0.03, shrink=0.6)
    cb.set_label("Partial Spearman correlation between social advantage and target attainment (net of log GDP per capita)",
                 fontsize=6.5)
    _panel(ax, "a", x=-0.28, y=1.12)
    axs = fig.add_subplot(gs[1], sharey=ax)
    summ = R["DM"]["summary"].reindex(SOC_ORDER)
    yy = np.arange(len(SOC_ORDER))
    axs.barh(yy - 0.18, summ["n_convergent"], height=0.34, color=COL["convergent"], label="Convergent")
    axs.barh(yy + 0.18, -summ["n_divergent"], height=0.34, color=COL["divergent"], hatch="////", edgecolor="white",
             lw=0, label="Divergent")
    axs.axvline(0, color="0.3", lw=0.6)
    axs.set_xlim(-4, 8)
    axs.set_xlabel("Number of targets")
    axs.tick_params(axis="y", left=False, labelleft=False)
    for sp in ("top", "right", "left"):
        axs.spines[sp].set_visible(False)
    axs.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.45, 1.0), fontsize=6)
    for D, yv in dim_pos:
        axs.text(8.3, yv, DIM_SHORT[D], ha="left", va="center", fontsize=6.5, fontweight="bold", color="0.25")
        axs.plot([8.1, 8.1], [yv - 0.42 * sum(SOCIAL[x][1] == D for x in SOC), yv + 0.42 * sum(SOCIAL[x][1] == D for x in SOC)],
                 color=DIM_COL[D], lw=2, clip_on=False)
    _panel(axs, "b", x=-0.05, y=1.07)
    save_figure(fig, path)


# ---------------------------------------------------------------------------------------------------------------
def figure_5_quantile_profiles(R, path):
    """Quantile-regression coefficients of social deprivation on SDG 3 attainment."""
    QM = R["QM"]
    fig, axs = plt.subplots(1, 3, figsize=(174 * MM, 68 * MM), gridspec_kw=dict(width_ratios=[1, 1, 1.15], wspace=0.42))
    ax = axs[0]
    t = QM["main"]["table"]
    ax.fill_between(t.tau, t.ci_low, t.ci_high, color="#0072B2", alpha=0.2, lw=0)
    ax.plot(t.tau, t.beta, "o-", color="#0072B2", ms=3, lw=1, label="Quantile regression")
    o = QM["main"]["ols"]
    ax.axhline(o["beta"], color="black", lw=0.8, ls="--", label="OLS")
    ax.axhspan(o["ci"][0], o["ci"][1], color="0.5", alpha=0.12, lw=0, hatch="////")
    ax.axhline(0, color="0.5", lw=0.5)
    ax.set_xlabel("Quantile of SDG 3 attainment (τ)")
    ax.set_ylabel("Change in attainment (points) per\n1-point higher deprivation score")
    ax.legend(frameon=False, loc="lower right", fontsize=6)
    _panel(ax, "a", x=-0.25)
    ax = axs[1]
    sty = {"Maternal, child and coverage targets": ("#0072B2", "o-", ""),
           "Infectious-disease targets": ("#D55E00", "s--", "")}
    for f, r in QM["families"].items():
        tt = r["table"]
        c, m, _ = sty[f]
        ax.fill_between(tt.tau, tt.ci_low, tt.ci_high, color=c, alpha=0.15, lw=0)
        ax.plot(tt.tau, tt.beta, m, color=c, ms=3, lw=1, label=f.replace(" targets", ""))
    ax.axhline(0, color="0.5", lw=0.5)
    ax.set_xlabel("Quantile of family attainment (τ)")
    ax.set_ylim(-1.05, 1.05)
    ax.legend(frameon=False, loc="upper right", fontsize=6)
    _panel(ax, "b", x=-0.25)
    ax = axs[2]
    mk = {0.25: ("v", "#D55E00"), 0.5: ("o", "0.2"), 0.75: ("^", "#0072B2")}
    for i, D in enumerate(DIMENSIONS):
        tt = QM["dimensions"][D]["table"]
        for k, r in enumerate(tt.itertuples()):
            m_, c = mk[r.tau]
            yv = i + (k - 1) * 0.24
            ax.plot([r.ci_low, r.ci_high], [yv, yv], color=c, lw=0.8)
            ax.plot(r.beta, yv, m_, color=c, ms=3.5, label=f"τ = {r.tau}" if i == 0 else None)
    ax.axvline(0, color="0.5", lw=0.5)
    ax.set_yticks(range(len(DIMENSIONS)))
    ax.set_yticklabels([DIM_SHORT[D] for D in DIMENSIONS])
    ax.invert_yaxis()
    ax.set_xlabel("Change in attainment (points) per\n1 SD higher dimension disadvantage")
    ax.legend(frameon=False, fontsize=6, loc="lower right")
    _panel(ax, "c", x=-0.3)
    for a in axs:
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    save_figure(fig, path)


# ---------------------------------------------------------------------------------------------------------------
def figure_6_policy_priorities(R, path):
    """(a) First social-policy entry point by country; (b) SDG 1.2-style halving scenario."""
    PL = R["PL"]
    fig = plt.figure(figsize=(174 * MM, 140 * MM))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1], wspace=0.25)
    ax = fig.add_subplot(gs[0])
    cats = {D: (DIM_COL[D], DIM_HATCH[D]) for D in DIMENSIONS}
    cats["No gap below the regional median"] = ("white", "")
    _map(R, ax, PL["priorities"]["priority_1"], categorical=cats)
    counts = PL["priority_counts"]
    handles = [Patch(fc=DIM_COL[D], hatch=DIM_HATCH[D], ec="0.25", label=f"{DIM_SHORT[D]} ({int(counts.get(D, 0))})")
               for D in DIMENSIONS if counts.get(D, 0) > 0]
    if counts.get("No gap below the regional median", 0):
        handles.append(Patch(fc="white", ec="0.25", label=f"No gap ({int(counts['No gap below the regional median'])})"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.06), ncol=3, frameon=False, fontsize=6,
              title="First social-policy entry point (number of countries)", title_fontsize=6.5)
    _panel(ax, "a", x=0.02, y=0.98)
    ax = fig.add_subplot(gs[1])
    sc = PL["scenario"].sort_values("attainment")
    pri = PL["priorities"].loc[sc.index, "priority_1"]
    y = np.arange(len(sc))
    for i, (c, r) in enumerate(sc.iterrows()):
        col = DIM_COL.get(pri[c], "0.6")
        ax.plot([r.attainment, r.attainment_scenario], [i, i], color=col, lw=1.4, solid_capstyle="butt")
        ax.plot(r.attainment, i, "o", color="0.3", ms=2.2)
        ax.plot(r.attainment + r.gain_ols, i, "|", color="black", ms=3.2, mew=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels([_nm(c) for c in sc.index], fontsize=5.8)
    ax.set_ylim(-0.8, len(sc) - 0.2)
    ax.set_xlim(20, 100)
    ax.set_xlabel("Mean SDG 3 target attainment (points)")
    ax.legend(handles=[Line2D([], [], marker="o", color="0.3", ls="", ms=3, label="Observed"),
                       Line2D([], [], color="0.4", lw=1.4, label="Gain, quantile slope"),
                       Line2D([], [], marker="|", color="black", ls="", ms=4, label="Gain, OLS slope")],
              frameon=False, fontsize=6, loc="lower right")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)
    _panel(ax, "b", x=-0.12, y=1.0)
    save_figure(fig, path)
