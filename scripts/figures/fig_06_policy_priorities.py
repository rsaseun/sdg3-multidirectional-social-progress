"""Fig. 6: Policy entry points and the SDG 1.2 halving scenario.

Regenerates outputs/figures/Fig6.png and .tif (600 dpi, RGB) from the cached results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _bootstrap import load_results, FIG_DIR  # noqa: E402
from sdg3_social_directions.figures import figure_6_policy_priorities  # noqa: E402

if __name__ == "__main__":
    figure_6_policy_priorities(load_results(), FIG_DIR / "Fig6")
    print("Saved", FIG_DIR / "Fig6.png")
