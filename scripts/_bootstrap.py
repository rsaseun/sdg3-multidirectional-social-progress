"""Shared helpers for the scripts: import path, output folders and the cached results."""
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sdg3_social_directions.config import OUT_DIR  # noqa: E402
from sdg3_social_directions import analysis, data  # noqa: E402

FIG_DIR = OUT_DIR / "figures"
TAB_DIR = OUT_DIR / "tables"
CACHE = OUT_DIR / "cache" / "results.pkl"


def run_and_cache():
    """Run the full analysis, write numerical results and cache the results dictionary."""
    d = data.load_data()
    geo = data.load_geometries()
    R = analysis.run_analysis(d, geo)
    analysis.save_results(R, OUT_DIR)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE, "wb") as f:
        pickle.dump(R, f)
    return R


def load_results():
    """Load cached results, running the analysis first if no cache exists."""
    if CACHE.exists():
        with open(CACHE, "rb") as f:
            return pickle.load(f)
    return run_and_cache()


def save_table(tb, name):
    """Write one table as CSV and as an editable Word file."""
    from sdg3_social_directions.docx_tables import write_tables_docx
    TAB_DIR.mkdir(parents=True, exist_ok=True)
    tb["df"].to_csv(TAB_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")
    write_tables_docx([tb], TAB_DIR / f"{name}.docx")
