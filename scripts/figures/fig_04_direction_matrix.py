"""Fig. 4: Directional association matrix (convergent / divergent).

Regenerates outputs/figures/Fig4.png and .tif (600 dpi, RGB) from the cached results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _bootstrap import load_results, FIG_DIR  # noqa: E402
from sdg3_social_directions.figures import figure_4_direction_matrix  # noqa: E402

if __name__ == "__main__":
    figure_4_direction_matrix(load_results(), FIG_DIR / "Fig4")
    print("Saved", FIG_DIR / "Fig4.png")
