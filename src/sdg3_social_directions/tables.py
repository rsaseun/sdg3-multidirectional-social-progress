"""One function per table. Each returns dict(label, title, df, note, widths) for CSV and Word output.

``write_online_resource`` writes Online Resource 1 (all supporting results) as an .xlsx workbook.
"""
import numpy as np
import pandas as pd

from .analysis import FAMILY, SOC
from .config import (CUTOFF_SENS, DIM_SHORT, DIMENSIONS, K_GRID, N_BOOT_CORR, Q_FDR, SOCIAL, STABLE, TARGET_UNITS,
                     TARGETS)

SOURCE = {"POV": "World Bank Poverty and Inequality Platform", "FIES": "FAO (SDG 2.1.2)", "FSCH": "UNDP HDR 2025",
          "CHILDMAR": "UNICEF (SDG 5.3.1)", "SIGI": "OECD SIGI 2023", "GINI": "World Bank WDI",
          "UNEMP": "ILO modelled estimates (WDI)", "EXCL_EPR": "Ethnic Power Relations", "EXCL_VDEM": "V-Dem",
          "TRUST": "Afrobarometer Round 9", "WATERCOLL": "World Bank / WHO–UNICEF JMP",
          "MMR": "WHO et al.", "SBA": "UNICEF", "U5MR": "UN IGME", "NMR": "UN IGME", "HIV": "UNAIDS", "TB": "WHO",
          "FP": "UN DESA", "ABR": "WHO / UN DESA", "SCI": "WHO", "DTP3": "WHO–UNICEF"}

POLICY = {
    "Voice and inclusion": ("Equitable allocation formulas for primary care and maternal–child services that weight "
                            "excluded regions and groups; community scorecards and health committees with seats for "
                            "excluded groups; disaggregated SDG 3 reporting by ethnic and regional group.",
                            "Start with budget formulas in 2026–2027; publish group-disaggregated progress yearly"),
    "Education": ("Keep girls in school through secondary level (fee abolition, cash transfers conditional on "
                  "enrolment, school-based sexual and reproductive health education); adult literacy linked to "
                  "antenatal and child-health contacts.",
                  "Effects on mortality lag; protect education budgets now to matter by 2030"),
    "Gender equity and autonomy": ("Enforce 18 as the minimum marriage age without exceptions; reform discriminatory "
                                   "family and inheritance law; adolescent-friendly contraception; women's "
                                   "decision-making in health-care use.",
                                   "Pair legal reform with community dialogue and adolescent services"),
    "Social cohesion and care": ("Rebuild trust through community health workers recruited locally, transparent "
                                 "complaint and redress mechanisms and continuity of immunisation outreach; household "
                                 "water connections that cut women's and girls' collection time.",
                                 "Fast, visible delivery builds trust; link water projects to clinic catchments"),
    "Distribution and work": ("Progressive social protection and youth employment programmes in high-inequality, "
                              "high-unemployment settings, integrated with HIV and tuberculosis prevention and "
                              "case finding; social health insurance subsidies for informal workers.",
                              "Target HIV and TB gains without crowding out maternal–child coverage"),
    "Material living standards": ("Scale shock-responsive cash transfers and school feeding; link transfer "
                                  "registries to fee exemptions for maternal and child care and to TB nutrition "
                                  "support.",
                                  "Use existing registries for rapid scale-up in 2026–2027"),
}


def _fmt(x, d=2):
    return "" if pd.isna(x) else f"{x:.{d}f}"


def _cut(s, z):
    unit = SOCIAL[s][3]
    worse = SOCIAL[s][2]
    v = z[s]
    txt = f"{v:.2f}" if abs(v) < 2 else f"{v:.1f}"
    return f"{'>' if worse > 0 else '<'} {txt} ({unit.split('(')[0].strip()})"


# ---------------------------------------------------------------------------------------------------------------
def table_1_indicators(R):
    """Social indicators with Alkire–Foster cutoffs and SDG 3 targets with thresholds."""
    d, z = R["d"], R["SD"]["AF"]["z"]
    rows = []
    for D in DIMENSIONS:
        for s in [x for x in SOC if SOCIAL[x][1] == D]:
            rows.append({"Domain": D, "Indicator": SOCIAL[s][0], "Unit": SOCIAL[s][3],
                         "Cutoff (median) or target": _cut(s, z).split(" (")[0],
                         "Red": "", "n": int(d[s].notna().sum()), "Source": SOURCE[s]})
    for t, (lab, code, sign, green, red, low) in TARGETS.items():
        fam = "SDG 3: maternal, child and coverage" if t in FAMILY["Maternal, child and coverage targets"] \
            else "SDG 3: infectious disease"
        rows.append({"Domain": fam, "Indicator": f"{lab} ({code})", "Unit": TARGET_UNITS[t],
                     "Cutoff (median) or target": f"{'≥' if sign > 0 else '≤'} {green:g}",
                     "Red": f"{'<' if sign > 0 else '>'} {red:g}", "n": int(d[t].notna().sum()),
                     "Source": SOURCE[t]})
    df = pd.DataFrame(rows)
    df.loc[df["Domain"].duplicated(), "Domain"] = ""
    note = ("Social indicators: a country is deprived when it is worse than the regional median of the 48 countries. "
            "Each of the six domains carries one-sixth of the weight, shared equally by its indicators; weights are "
            "renormalised over the indicators available for each country. SDG 3 targets: target (green) and red "
            "thresholds, and the lower bounds used to scale attainment from 0 to 1, follow the Sustainable "
            "Development Report 2026 (Sachs et al. 2026); the vaccination threshold is applied to DTP3. "
            "EPR, Ethnic Power Relations; FIES, Food Insecurity Experience Scale; SIGI, Social Institutions and Gender "
            "Index; UHC, universal health coverage; DTP3, third dose of diphtheria–tetanus–pertussis vaccine.")
    return dict(label="Table 1", title="Social dimensions and SDG 3 targets analysed", df=df, note=note,
                widths=[3.4, 4.6, 4.4, 2.4, 1.3, 0.9, 4.6])


def table_2_social_deprivation(R):
    """Alkire–Foster results: headline measures, dimensional contributions and sensitivity."""
    SD = R["SD"]
    AF, ci = SD["AF"], SD["ci"]
    rows = [("Headline (median cutoffs, k = 1/3)", "Countries identified as socially deprived", f"{int(AF['identified'].sum())} of {len(R['d'])}"),
            ("", "Headcount ratio H", f"{AF['H']:.3f} ({ci['H'][0]:.3f}–{ci['H'][1]:.3f})"),
            ("", "Intensity A", f"{AF['A']:.3f} ({ci['A'][0]:.3f}–{ci['A'][1]:.3f})"),
            ("", "Adjusted headcount ratio M0 = H × A", f"{AF['M0']:.3f} ({ci['M0'][0]:.3f}–{ci['M0'][1]:.3f})"),
            ("", "Adjusted gap measure M1", f"{AF['M1']:.3f}"),
            ("", "Share of regional population in identified countries", f"{SD['H_pop'] * 100:.1f}%")]
    first = True
    for D in DIMENSIONS:
        rows.append(("Contribution to M0 (%)" if first else "", D, f"{AF['contrib'][D]:.1f}"))
        first = False
    sens = SD["sensitivity"]
    first = True
    for lab in CUTOFF_SENS:
        s = sens[sens.cutoff == lab].set_index("k")
        txt = "; ".join(f"k = {k:.2f}: H {s.loc[k, 'H']:.2f}, M0 {s.loc[k, 'M0']:.2f}" for k in K_GRID)
        rows.append(("Sensitivity (cutoff rule)" if first else "", f"Cutoff at {lab}", txt))
        first = False
    ra = SD["rank_agree"].values[np.triu_indices(3, 1)]
    rows.append(("Rank stability", "Spearman correlation of country scores across cutoff rules",
                 f"{ra.min():.2f}–{ra.max():.2f}"))
    rows.append(("", "Spearman correlation, nested vs equal indicator weights", f"{SD['rank_agree_weights']:.2f}"))
    df = pd.DataFrame(rows, columns=["Measure group", "Measure", "Value (95% bootstrap interval)"])
    note = (f"Intervals: {N_BOOT_CORR:,} country bootstrap resamples, re-estimating the cutoffs in each resample. "
            "k is the share of weighted indicators in which a country must be deprived to be identified. Contributions "
            "above 16.7% (one-sixth) indicate that a domain contributes more than its weight.")
    return dict(label="Table 2", title="Multidimensional social deprivation across 48 Sub-Saharan African countries",
                df=df, note=note, widths=[4.0, 8.0, 12.0])


def table_3_directions(R):
    """Direction profile of each social indicator across the ten SDG 3 targets."""
    mx, summ = R["DM"]["matrix"], R["DM"]["summary"]
    lab = {t: TARGETS[t][1] for t in TARGETS}
    rows = []
    for D in DIMENSIONS:
        for s in [x for x in SOC if SOCIAL[x][1] == D]:
            m = mx[mx.social == s]
            conv = m[m.direction == "convergent"].sort_values("r", ascending=False)
            div = m[m.direction == "divergent"].sort_values("r")
            rows.append({"Domain": DIM_SHORT[D], "Social indicator (advantage direction)": SOCIAL[s][0],
                         "Convergent targets (ρ)": "; ".join(f"{lab[t]} ({r:.2f})" for t, r in zip(conv.target, conv.r)) or "–",
                         "Divergent targets (ρ)": "; ".join(f"{lab[t]} ({r:.2f})" for t, r in zip(div.target, div.r)) or "–",
                         "Mean ρ": _fmt(summ.loc[s, "mean_r"]), "Profile": summ.loc[s, "profile"]})
    df = pd.DataFrame(rows)
    df.loc[df["Domain"].duplicated(), "Domain"] = ""
    ag = R["DM"]["agreement"]
    note = ("ρ, partial Spearman correlation between social advantage (lower poverty, more schooling, and so on) and "
            "target attainment, net of log GDP per capita. A pair is convergent or divergent when the "
            f"Benjamini–Hochberg q < {Q_FDR:.2f} across all 110 pairs and at least {STABLE:.0%} of {N_BOOT_CORR:,} "
            "bootstrap resamples share the sign of ρ. Sign agreement with the main matrix: unadjusted "
            f"{ag['unadjusted']['sign_agreement']:.0%}; additionally adjusted for urbanisation "
            f"{ag['adjusted for income and urbanisation']['sign_agreement']:.0%}; excluding the ten countries with the "
            f"highest HIV incidence {ag['excluding high-HIV decile']['sign_agreement']:.0%}. Target codes as in Table 1.")
    return dict(label="Table 3", title="Convergent and divergent directions linking social dimensions to SDG 3 targets",
                df=df, note=note, widths=[2.2, 4.2, 7.2, 4.6, 1.4, 2.4])


def table_4_policy_portfolio(R):
    """Country entry points, linked targets and policy instruments for 2026–2030."""
    PL, DM = R["PL"], R["DM"]
    dm = DM["dim_matrix"]
    lab = {t: TARGETS[t][1] for t in TARGETS}
    pri = PL["priorities"]["priority_1"]
    rows = []
    for D in sorted(DIMENSIONS, key=lambda x: -int((pri == x).sum())):
        cs = sorted(pri.index[pri == D])
        if not cs:
            continue
        m = dm[dm.social == D]
        conv = ", ".join(lab[t] for t in m[m.direction == "convergent"].sort_values("r", ascending=False).target) or "–"
        div = ", ".join(lab[t] for t in m[m.direction == "divergent"].target) or "–"
        g = PL["scenario"].loc[cs, "gain_quantile"].mean()
        rows.append({"Entry point": D, "First entry point in": f"{len(cs)}: " + ", ".join(cs),
                     "Convergent targets": conv, "Divergent links": div,
                     "Gain (points)": f"{g:.1f}",
                     "Policy instruments, 2026–2030": POLICY[D][0], "Implementation direction": POLICY[D][1]})
    df = pd.DataFrame(rows)
    note = ("Entry point: the domain with the largest gap-weighted multi-target leverage in each country (normalised "
            "deprivation gap × sum over targets of the dimension-level convergent correlation weighted by the "
            "country's remaining distance to target, minus divergent links). Gains: SDG 1.2-style halving of each "
            "country's deprivation score, using the quantile-regression slope at the country's position in the "
            "conditional distribution (mean for the countries listed); associations, not causal effects. Divergent "
            "links: targets with a divergent dimension-level association, to be monitored. "
            + (f"{', '.join(pri.index[pri == 'No gap below the regional median'])} had no deprivation gap below the "
               "regional median." if (pri == 'No gap below the regional median').any() else ""))
    return dict(label="Table 4", title="Social policy portfolio for the SDG 3 targets before 2030", df=df, note=note,
                widths=[2.4, 5.0, 2.2, 1.7, 1.4, 6.6, 3.4])


TABLES = {"Table_1": table_1_indicators, "Table_2": table_2_social_deprivation, "Table_3": table_3_directions,
          "Table_4": table_4_policy_portfolio}


# ---------------------------------------------------------------------------------------------------------------
def online_resource_sheets(R):
    """All supporting results as {sheet name: DataFrame} for Online Resource 1."""
    d = R["d"]
    A, S, att = R["A"], R["status"], R["att"]
    SD, DM, QM, PL = R["SD"], R["DM"], R["QM"], R["PL"]
    readme = pd.DataFrame({"Sheet": ["S1_attainment", "S2_target_status", "S3_deprivation", "S4_cutoffs",
                                     "S5_AF_sensitivity", "S6_codeprivation", "S7_direction_matrix",
                                     "S8_direction_dimensions", "S9_direction_sensitivity", "S10_quantile_main",
                                     "S11_quantile_families", "S12_quantile_dimensions", "S13_policy_leverage",
                                     "S14_halving_scenario"],
                           "Content": ["Target attainment (0–1) by country and target, with mean attainment",
                                       "Target status: 2 achieved, 1 challenges remain, 0 red (SDR 2026 thresholds)",
                                       "Alkire–Foster deprivation matrix g0 (1 = deprived) and country scores",
                                       "Indicator cutoffs (regional medians)",
                                       "H, A, M0 and M1 across cutoff rules and k",
                                       "Co-deprivation of domain pairs (lift relative to independence)",
                                       "Partial Spearman correlations, intervals, p, q, sign stability, direction",
                                       "Dimension-level direction matrix used for policy leverage",
                                       "Direction matrices under three sensitivity specifications",
                                       "Quantile and OLS coefficients, mean attainment",
                                       "Quantile coefficients by target family",
                                       "Quantile coefficients by social domain (τ = 0.25, 0.50, 0.75)",
                                       "Gap-weighted leverage by country and domain, with first and second entry points",
                                       "SDG 1.2-style halving scenario by country"]})
    s1 = A.mul(100).round(1).join(att.round(1))
    s3 = SD["AF"]["g0"].join(SD["country"])
    s4 = pd.DataFrame({"indicator": SOC, "label": [SOCIAL[s][0] for s in SOC], "cutoff": SD["AF"]["z"].values,
                       "higher_is_worse": [SOCIAL[s][2] > 0 for s in SOC]})
    sens = pd.concat({k: v for k, v in DM["sensitivity"].items()}, names=["specification"]).reset_index(level=0)
    fam = pd.concat({f: r["table"] for f, r in QM["families"].items()}, names=["family"]).reset_index(level=0)
    dims = pd.concat({D: r["table"] for D, r in QM["dimensions"].items()}, names=["domain"]).reset_index(level=0)
    qm = QM["main"]["table"].copy()
    qm["ols_beta"], qm["ols_ci_low"], qm["ols_ci_high"] = QM["main"]["ols"]["beta"], *QM["main"]["ols"]["ci"]
    lev = PL["leverage"].round(4).join(PL["priorities"])
    return {"README": readme, "S1_attainment": s1.reset_index(), "S2_target_status": S.reset_index(),
            "S3_deprivation": s3.reset_index(), "S4_cutoffs": s4, "S5_AF_sensitivity": SD["sensitivity"],
            "S6_codeprivation": SD["codeprivation"], "S7_direction_matrix": DM["matrix"],
            "S8_direction_dimensions": DM["dim_matrix"], "S9_direction_sensitivity": sens,
            "S10_quantile_main": qm, "S11_quantile_families": fam, "S12_quantile_dimensions": dims,
            "S13_policy_leverage": lev.reset_index(), "S14_halving_scenario": PL["scenario"].reset_index(),
            "data_used": d.reset_index()}


def write_online_resource(R, path, header=None):
    """Write Online Resource 1 as an .xlsx workbook (one sheet per supporting result)."""
    sheets = online_resource_sheets(R)
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        if header:
            pd.DataFrame({"": header}).to_excel(xw, sheet_name="README", index=False, header=False)
            sheets["README"].to_excel(xw, sheet_name="README", index=False, startrow=len(header) + 1)
        else:
            sheets["README"].to_excel(xw, sheet_name="README", index=False)
        for name, df in sheets.items():
            if name != "README":
                df.to_excel(xw, sheet_name=name[:31], index=False)
