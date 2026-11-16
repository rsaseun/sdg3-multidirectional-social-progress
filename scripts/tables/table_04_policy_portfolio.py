"""Table 4: Social policy portfolio before 2030.

Regenerates outputs/tables/Table_4.csv and .docx from the cached results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _bootstrap import load_results, save_table  # noqa: E402
from sdg3_social_directions.tables import table_4_policy_portfolio  # noqa: E402

if __name__ == "__main__":
    save_table(table_4_policy_portfolio(load_results()), "Table_4")
    print("Saved outputs/tables/Table_4.csv and .docx")
