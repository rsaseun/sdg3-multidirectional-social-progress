"""Load the compiled country dataset and map geometries."""
import json

import geopandas as gpd
import numpy as np
import pandas as pd

from .config import DATA_DIR


def load_data(data_dir=DATA_DIR):
    """Country-level DataFrame indexed by country, with log GDP per capita added."""
    d = pd.read_csv(data_dir / "sdg3_ssa_country_data.csv", index_col="country", float_precision="round_trip")
    d["lnGDP"] = np.log(d["GDPPC"])
    return d


def _read_geojson(path):
    with open(path, encoding="utf-8") as f:
        gj = json.load(f)
    return gpd.GeoDataFrame.from_features(gj["features"], crs="EPSG:4326")


def load_geometries(data_dir=DATA_DIR):
    """(48 SSA countries with a 'country' column, surrounding context countries) for maps."""
    return _read_geojson(data_dir / "ssa_countries.geojson"), _read_geojson(data_dir / "africa_context.geojson")
