"""Online Resource 1: all supporting results as an .xlsx workbook (outputs/tables/ESM_1.xlsx)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _bootstrap import load_results, TAB_DIR  # noqa: E402
from sdg3_social_directions.tables import write_online_resource  # noqa: E402

if __name__ == "__main__":
    write_online_resource(load_results(), TAB_DIR / "ESM_1.xlsx")
    print("Saved", TAB_DIR / "ESM_1.xlsx")
