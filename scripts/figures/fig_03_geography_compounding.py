"""Fig. 3: Map of deprivation, domain contributions, co-deprivation lift.

Regenerates outputs/figures/Fig3.png and .tif (600 dpi, RGB) from the cached results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _bootstrap import load_results, FIG_DIR  # noqa: E402
from sdg3_social_directions.figures import figure_3_geography_compounding  # noqa: E402

if __name__ == "__main__":
    figure_3_geography_compounding(load_results(), FIG_DIR / "Fig3")
    print("Saved", FIG_DIR / "Fig3.png")
