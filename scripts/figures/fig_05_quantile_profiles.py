"""Fig. 5: Quantile-regression profiles.

Regenerates outputs/figures/Fig5.png and .tif (600 dpi, RGB) from the cached results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _bootstrap import load_results, FIG_DIR  # noqa: E402
from sdg3_social_directions.figures import figure_5_quantile_profiles  # noqa: E402

if __name__ == "__main__":
    figure_5_quantile_profiles(load_results(), FIG_DIR / "Fig5")
    print("Saved", FIG_DIR / "Fig5.png")
