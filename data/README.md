# Data

`sdg3_ssa_country_data.csv` has one row per country (the 48 Sub-Saharan African economies of the World Bank
classification) and 24 columns: 11 social indicators in six capability domains, 10 SDG 3 indicators, and GDP per
capita, urbanisation and population. Values are the most recent public estimates from United Nations custodian
agencies, the World Bank and other international sources, compiled for the study; missing values are left empty.
`codebook.csv` gives each variable's label, unit, role in the analysis, source and number of missing countries.

SDG 3 target thresholds (target, red threshold and lower bound) follow the Sustainable Development Report 2026
(Sachs et al. 2026, Table 5.4) and are set in `src/sdg3_social_directions/config.py`.

Map boundaries (`*.geojson`, EPSG:4326) are derived from Natural Earth (public domain) and are used only for maps.
