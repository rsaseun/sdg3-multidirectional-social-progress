"""Table 1: Social dimensions and SDG 3 targets analysed.

Regenerates outputs/tables/Table_1.csv and .docx from the cached results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _bootstrap import load_results, save_table  # noqa: E402
from sdg3_social_directions.tables import table_1_indicators  # noqa: E402

if __name__ == "__main__":
    save_table(table_1_indicators(load_results()), "Table_1")
    print("Saved outputs/tables/Table_1.csv and .docx")
