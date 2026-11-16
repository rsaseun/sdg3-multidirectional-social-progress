"""Table 2: Multidimensional social deprivation (H, A, M0, contributions, sensitivity).

Regenerates outputs/tables/Table_2.csv and .docx from the cached results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _bootstrap import load_results, save_table  # noqa: E402
from sdg3_social_directions.tables import table_2_social_deprivation  # noqa: E402

if __name__ == "__main__":
    save_table(table_2_social_deprivation(load_results()), "Table_2")
    print("Saved outputs/tables/Table_2.csv and .docx")
