"""Table 3: Convergent and divergent directions by social indicator.

Regenerates outputs/tables/Table_3.csv and .docx from the cached results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _bootstrap import load_results, save_table  # noqa: E402
from sdg3_social_directions.tables import table_3_directions  # noqa: E402

if __name__ == "__main__":
    save_table(table_3_directions(load_results()), "Table_3")
    print("Saved outputs/tables/Table_3.csv and .docx")
