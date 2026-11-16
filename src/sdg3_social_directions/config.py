"""Paths, indicator definitions, analysis constants and plotting style."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "outputs"
DPI, MM = 600, 1 / 25.4

# ---------------------------------------------------------------------------------------------------------------
# Social dimensions (capability domains). code -> (label, dimension, +1 if a higher value is worse, unit)
# ---------------------------------------------------------------------------------------------------------------
SOCIAL = {
    "POV": ("Extreme poverty", "Material living standards", +1, "% below US$3.00/day (2021 PPP)"),
    "FIES": ("Food insecurity", "Material living standards", +1, "% moderate or severe (FIES)"),
    "FSCH": ("Female schooling", "Education", -1, "mean years, women 25+"),
    "CHILDMAR": ("Child marriage", "Gender equity and autonomy", +1, "% women 20–24 married before 18"),
    "SIGI": ("Discriminatory social institutions", "Gender equity and autonomy", +1, "SIGI score (0–100)"),
    "GINI": ("Income inequality", "Distribution and work", +1, "Gini index"),
    "UNEMP": ("Unemployment", "Distribution and work", +1, "% labour force"),
    "EXCL_EPR": ("Politically excluded groups", "Voice and inclusion", +1, "% population (EPR)"),
    "EXCL_VDEM": ("Exclusion by social group", "Voice and inclusion", +1, "V-Dem index (0–1)"),
    "TRUST": ("Interpersonal and institutional trust", "Social cohesion and care", -1, "% trusting"),
    "WATERCOLL": ("Water collection by women and girls", "Social cohesion and care", +1, "% households"),
}
# short deprivation-framed labels for figures
SOC_SHORT = {"POV": "Extreme poverty", "FIES": "Food insecurity", "FSCH": "Low female\nschooling",
             "CHILDMAR": "Child marriage", "SIGI": "Discriminatory\ninstitutions", "GINI": "Income\ninequality",
             "UNEMP": "Unemployment", "EXCL_EPR": "Political\nexclusion", "EXCL_VDEM": "Group\nexclusion",
             "TRUST": "Low trust", "WATERCOLL": "Water collection\nby women/girls"}
DIMENSIONS = ["Material living standards", "Education", "Gender equity and autonomy", "Distribution and work",
              "Voice and inclusion", "Social cohesion and care"]
DIM_SHORT = {"Material living standards": "Material", "Education": "Education", "Gender equity and autonomy": "Gender",
             "Distribution and work": "Distribution", "Voice and inclusion": "Voice", "Social cohesion and care": "Cohesion"}

# ---------------------------------------------------------------------------------------------------------------
# SDG 3 targets. code -> (label, SDG indicator, +1 if higher is better, green threshold (target), red threshold,
# lower bound). Thresholds and bounds: Sustainable Development Report 2026, Table 5.4 (DTP3 uses the vaccine row).
# ---------------------------------------------------------------------------------------------------------------
TARGETS = {
    "MMR": ("Maternal mortality", "3.1.1", -1, 70, 140, 814),
    "SBA": ("Skilled birth attendance", "3.1.2", +1, 98, 90, 23),
    "U5MR": ("Under-five mortality", "3.2.1", -1, 25, 50, 130),
    "NMR": ("Neonatal mortality", "3.2.2", -1, 12, 18, 40),
    "HIV": ("HIV incidence", "3.3.1", -1, 0.2, 1.0, 5.5),
    "TB": ("Tuberculosis incidence", "3.3.2", -1, 10, 75, 561),
    "FP": ("Family planning (modern methods)", "3.7.1", +1, 80, 60, 30),
    "ABR": ("Adolescent births", "3.7.2", -1, 25, 50, 140),
    "SCI": ("UHC service coverage", "3.8.1", +1, 80, 60, 38),
    "DTP3": ("DTP3 immunisation", "3.b.1", +1, 90, 80, 41),
}
TARGET_UNITS = {"MMR": "per 100,000 live births", "SBA": "% births", "U5MR": "per 1,000 live births",
                "NMR": "per 1,000 live births", "HIV": "per 1,000 uninfected", "TB": "per 100,000",
                "FP": "% women with demand", "ABR": "per 1,000 women 15–19", "SCI": "index (0–100)", "DTP3": "% infants"}

# Alkire–Foster settings: indicator cutoff = regional median (relative deprivation); dual cutoff k = 1/3
CUTOFF_RULE = "median"
K_MAIN = 1 / 3
K_GRID = [1 / 6, 1 / 4, 1 / 3, 1 / 2]
CUTOFF_SENS = {"median": 0.50, "worst 40%": 0.60, "worst third": 2 / 3}

# Inference settings
SEED = 2026
N_BOOT_CORR = 2000          # bootstrap resamples for sign stability of partial correlations
N_BOOT_QR = 1000            # bootstrap resamples for quantile-regression intervals
TAUS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
Q_FDR = 0.10                # Benjamini–Hochberg false discovery rate for classifying directions
STABLE = 0.90               # share of bootstrap resamples with the same sign
HALVING = 0.5               # SDG 1.2-style scenario: halve each country's social deprivation score

COL = {"convergent": "#0072B2", "divergent": "#D55E00", "neutral": "#BBBBBB"}
DIM_COL = {"Material living standards": "#E69F00", "Education": "#56B4E9", "Gender equity and autonomy": "#CC79A7",
           "Distribution and work": "#009E73", "Voice and inclusion": "#0072B2", "Social cohesion and care": "#D55E00"}
# hatching so that dimensions are distinguishable without colour (accessibility)
DIM_HATCH = {"Material living standards": "", "Education": "////", "Gender equity and autonomy": "....",
             "Distribution and work": "xxxx", "Voice and inclusion": "\\\\\\\\", "Social cohesion and care": "++"}


def _font():
    names = {f.name for f in font_manager.fontManager.ttflist}
    for f in ("Arial", "Helvetica", "Liberation Sans"):
        if f in names:
            return f
    return "DejaVu Sans"


def set_style():
    plt.rcParams.update({"font.family": _font(), "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
                         "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7, "axes.linewidth": 0.6,
                         "hatch.linewidth": 0.4, "svg.fonttype": "none", "pdf.fonttype": 42})
    return plt


def save_figure(fig, path):
    """Save a figure as a 600-dpi PNG and an LZW-compressed RGB TIFF with the same stem."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.with_suffix(".png"), dpi=DPI, facecolor="white", bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    with Image.open(path.with_suffix(".png")) as im:      # TIFF for submission: RGB, 8 bits per channel, LZW
        im.convert("RGB").save(path.with_suffix(".tif"), dpi=(DPI, DPI), compression="tiff_lzw")
