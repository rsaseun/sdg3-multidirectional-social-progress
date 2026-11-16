"""Reproduce every number, figure and table: python scripts/make_all.py [--use-cache]"""
import argparse
import time

from _bootstrap import run_and_cache, load_results, save_table, FIG_DIR, TAB_DIR
from sdg3_social_directions import figures, tables
from sdg3_social_directions.docx_tables import write_tables_docx

FIGURES = {
    "Fig1": "figure_1_framework",
    "Fig2": "figure_2_deprivation_profiles",
    "Fig3": "figure_3_geography_compounding",
    "Fig4": "figure_4_direction_matrix",
    "Fig5": "figure_5_quantile_profiles",
    "Fig6": "figure_6_policy_priorities",
}
TABLES = {
    "Table_1": "table_1_indicators",
    "Table_2": "table_2_social_deprivation",
    "Table_3": "table_3_directions",
    "Table_4": "table_4_policy_portfolio",
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--use-cache", action="store_true", help="reuse outputs/cache/results.pkl instead of re-running")
    a = ap.parse_args()
    t0 = time.time()
    R = load_results() if a.use_cache else run_and_cache()
    for name, func in FIGURES.items():
        getattr(figures, func)(R, FIG_DIR / name)
        print("figure", name)
    built = []
    for name, func in TABLES.items():
        tb = getattr(tables, func)(R)
        save_table(tb, name)
        built.append(tb)
        print("table", name)
    write_tables_docx(built, TAB_DIR / "All_Tables.docx")
    tables.write_online_resource(R, TAB_DIR / "ESM_1.xlsx")
    print(f"Done in {time.time() - t0:.0f} s. Outputs in outputs/")
