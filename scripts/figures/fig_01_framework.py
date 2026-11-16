"""Fig. 1: Conceptual framework: four directions of social progress.

Regenerates outputs/figures/Fig1.png and .tif (600 dpi, RGB) from the cached results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _bootstrap import load_results, FIG_DIR  # noqa: E402
from sdg3_social_directions.figures import figure_1_framework  # noqa: E402

if __name__ == "__main__":
    figure_1_framework(load_results(), FIG_DIR / "Fig1")
    print("Saved", FIG_DIR / "Fig1.png")
