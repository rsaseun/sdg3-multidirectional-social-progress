# sdg3-multidirectional-social-progress

**Social progress in many directions: multidimensional deprivation, divergent pathways and policy entry points for the health Sustainable Development Goal in Sub-Saharan Africa**

Manuscript submitted to *SN Social Sciences*. This repository contains the data, code and instructions needed to reproduce
every number, figure and table in the paper and its Online Resource 1.

## What the analysis does

The paper asks four questions about the social dimensions of progress towards the health Sustainable Development Goal
(SDG 3) in the 48 Sub-Saharan African economies of the World Bank classification:

| Research question | Method | Module |
|---|---|---|
| RQ1. How do social deprivations combine across countries? | Country-level **Alkire–Foster counting** of 11 indicators in six capability domains (regional-median cutoffs, k = 1/3, nested equal weights), H, A, M0, M1, domain contributions, co-deprivation lift, 2,000-resample bootstrap and cutoff/weight sensitivity | `analysis.social_deprivation` |
| RQ2. In which directions do social dimensions relate to the SDG 3 targets? | **Directional association matrix**: partial Spearman correlations (net of log GDP per capita) for 11 × 10 indicator–target pairs, Benjamini–Hochberg q < 0.10 and ≥ 90% bootstrap sign stability → convergent / divergent / undetermined; three sensitivity specifications | `analysis.directional_matrix` |
| RQ3. Does deprivation matter more for countries furthest behind? | **Quantile regression** (τ = 0.1–0.9) of mean target attainment on the deprivation score, by target family and by domain, with 1,000 paired bootstrap resamples | `analysis.quantile_models` |
| RQ4. Which policy entry points follow? | **Gap-weighted multi-target leverage** by country and domain; SDG 1.2-style **halving scenario** using the quantile slope at each country's conditional position | `analysis.policy_leverage` |

Target attainment uses the target (green) and red thresholds and lower bounds of the Sustainable Development Report 2026.
No composite health index is constructed.

## Repository structure

```
sdg3-multidirectional-social-progress/
├── data/
│   ├── sdg3_ssa_country_data.csv     48 countries × 24 variables (social indicators, SDG 3 indicators, controls)
│   ├── codebook.csv                  codes, labels, units, roles, sources, missing counts
│   ├── ssa_countries.geojson         map boundaries (EPSG:4326)
│   ├── africa_context.geojson        surrounding countries for maps
│   └── README.md
├── src/sdg3_social_directions/
│   ├── config.py        indicator definitions, SDR 2026 thresholds, settings, plotting style
│   ├── data.py          data loading
│   ├── analysis.py      all computations (run_analysis, save_results)
│   ├── figures.py       one function per figure
│   ├── tables.py        one function per table + Online Resource 1 workbook
│   └── docx_tables.py   editable Word tables (Springer style captions)
├── scripts/
│   ├── _bootstrap.py    import path, output folders, results cache
│   ├── 00_run_analysis.py
│   ├── make_all.py      runs everything
│   ├── online_resource_1.py
│   ├── figures/         one script per figure
│   └── tables/          one script per table
├── requirements.txt
├── CITATION.cff
├── LICENSE
└── README.md
```

## Quick start

```bash
git clone https://github.com/<your-username>/sdg3-multidirectional-social-progress.git
cd sdg3-multidirectional-social-progress
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/make_all.py                             # about 5 minutes (bootstrap resampling)
```

`make_all.py` runs the analysis, writes all numerical results to `outputs/results/` (CSV and `headline.json`), caches
them in `outputs/cache/results.pkl`, and regenerates all figures (`outputs/figures/`, 600-dpi PNG and TIFF), all tables
(`outputs/tables/`, CSV and editable Word, plus `All_Tables.docx`) and Online Resource 1 (`outputs/tables/ESM_1.xlsx`).
Individual outputs can be rebuilt from the cache:

```bash
python scripts/00_run_analysis.py
python scripts/figures/fig_04_direction_matrix.py
python scripts/tables/table_03_directions.py
python scripts/online_resource_1.py
python scripts/make_all.py --use-cache
```

## Figures

| Paper | Script | Function | Output | Content |
|---|---|---|---|---|
| Fig. 1 | `scripts/figures/fig_01_framework.py` | `sdg3_social_directions.figures.figure_1_framework` | `outputs/figures/Fig1.png/.tif` | Conceptual framework: four directions of social progress |
| Fig. 2 | `scripts/figures/fig_02_deprivation_profiles.py` | `sdg3_social_directions.figures.figure_2_deprivation_profiles` | `outputs/figures/Fig2.png/.tif` | Country deprivation profiles (Alkire–Foster matrix and scores) |
| Fig. 3 | `scripts/figures/fig_03_geography_compounding.py` | `sdg3_social_directions.figures.figure_3_geography_compounding` | `outputs/figures/Fig3.png/.tif` | Map of deprivation, domain contributions, co-deprivation lift |
| Fig. 4 | `scripts/figures/fig_04_direction_matrix.py` | `sdg3_social_directions.figures.figure_4_direction_matrix` | `outputs/figures/Fig4.png/.tif` | Directional association matrix (convergent / divergent) |
| Fig. 5 | `scripts/figures/fig_05_quantile_profiles.py` | `sdg3_social_directions.figures.figure_5_quantile_profiles` | `outputs/figures/Fig5.png/.tif` | Quantile-regression profiles |
| Fig. 6 | `scripts/figures/fig_06_policy_priorities.py` | `sdg3_social_directions.figures.figure_6_policy_priorities` | `outputs/figures/Fig6.png/.tif` | Policy entry points and the SDG 1.2 halving scenario |

## Tables

| Paper | Script | Function | Output | Content |
|---|---|---|---|---|
| Table 1 | `scripts/tables/table_01_indicators.py` | `sdg3_social_directions.tables.table_1_indicators` | `outputs/tables/Table_1.csv/.docx` | Social dimensions and SDG 3 targets analysed |
| Table 2 | `scripts/tables/table_02_social_deprivation.py` | `sdg3_social_directions.tables.table_2_social_deprivation` | `outputs/tables/Table_2.csv/.docx` | Multidimensional social deprivation (H, A, M0, contributions, sensitivity) |
| Table 3 | `scripts/tables/table_03_directions.py` | `sdg3_social_directions.tables.table_3_directions` | `outputs/tables/Table_3.csv/.docx` | Convergent and divergent directions by social indicator |
| Table 4 | `scripts/tables/table_04_policy_portfolio.py` | `sdg3_social_directions.tables.table_4_policy_portfolio` | `outputs/tables/Table_4.csv/.docx` | Social policy portfolio before 2030 |
| Online Resource 1 | `scripts/online_resource_1.py` | `sdg3_social_directions.tables.write_online_resource` | `outputs/tables/ESM_1.xlsx` | 14 sheets of supporting results |

## Main numerical outputs (`outputs/results/`)

| File | Content |
|---|---|
| `target_attainment.csv`, `target_status.csv`, `attainment_summary.csv` | Attainment (0–1), status and mean attainment by country |
| `af_country.csv`, `af_deprivation_matrix.csv`, `af_cutoffs.csv` | Alkire–Foster scores, identification, deprivation matrix and cutoffs |
| `af_sensitivity.csv`, `af_rank_agreement.csv`, `af_codeprivation.csv` | Sensitivity to cutoffs, k and weights; co-deprivation lift |
| `direction_matrix.csv`, `direction_matrix_dimensions.csv`, `direction_summary.csv` | Directional matrices and indicator profiles |
| `direction_matrix_sens_*.csv` | Sensitivity specifications |
| `qr_main.csv`, `qr_family_*.csv`, `qr_dimensions.csv` | Quantile-regression coefficients and intervals |
| `policy_leverage.csv`, `policy_priorities.csv`, `halving_scenario.csv` | Leverage, entry points and scenario |
| `headline.json` | Every number quoted in the text |

## Reproducibility

- All random steps use the seed in `config.py` (`SEED = 2026`) and a single NumPy generator, so results are identical
  across runs with the pinned versions in `requirements.txt` (Python 3.13). Nothing depends on wall-clock time or hash
  randomisation.
- Figures use Arial or Helvetica when installed, otherwise the metric-compatible Liberation Sans; only the font changes.
- The outputs were verified by running `make_all.py` on a clean copy of this repository and comparing every result file,
  table and figure with those used in the paper.

## Data

See `data/README.md` and `data/codebook.csv`. All values are public estimates from United Nations custodian agencies,
the World Bank and other international sources; please cite the original producers when reusing them. Map boundaries are
derived from Natural Earth (public domain).

## Citation

Please cite the paper and this repository (see `CITATION.cff`).

## Licence

Code: MIT (see `LICENSE`). Data: compiled from public sources under their original terms.
