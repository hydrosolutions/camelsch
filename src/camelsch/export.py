"""Export time series and attributes to CSV/Parquet."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

import geopandas as gpd
import pandas as pd

logger = logging.getLogger(__name__)

Format = Literal["csv", "parquet"]
GeoFormat = Literal["gpkg", "geojson"]


def export_timeseries(
    data: dict[str, pd.DataFrame],
    output: Path,
    fmt: Format = "csv",
) -> None:
    """Export time series dict to file(s).

    For parquet: single file with ``basin_id`` column.
    For CSV: single file if one basin, directory of files if multiple.
    """
    logger.debug("Exporting %d basin(s) as %s to %s", len(data), fmt, output)
    if fmt == "parquet":
        frames = []
        for bid, df in data.items():
            df = df.copy()
            df.insert(0, "basin_id", bid)
            frames.append(df)
        combined = pd.concat(frames)
        combined.to_parquet(output)
    else:
        if len(data) == 1:
            bid, df = next(iter(data.items()))
            df.to_csv(output)
        else:
            output.mkdir(parents=True, exist_ok=True)
            for bid, df in data.items():
                df.to_csv(output / f"basin_{bid}.csv")


def export_attributes(
    df: pd.DataFrame,
    output: Path,
    fmt: Format = "csv",
) -> None:
    """Export attributes DataFrame to file."""
    if fmt == "parquet":
        df.to_parquet(output)
    else:
        df.to_csv(output)


def export_merged(
    timeseries: dict[str, pd.DataFrame],
    attributes: pd.DataFrame,
    output: Path,
    fmt: Format = "parquet",
) -> None:
    """Export merged timeseries + attributes as flat analysis-ready file.

    Produces a dataset with columns: basin_id, date, <forcing_vars>, <target>, [<static_attrs>].
    Static attributes are repeated for each row of a given basin.
    """
    logger.debug("Exporting merged data for %d basin(s) as %s to %s", len(timeseries), fmt, output)
    frames = []
    for bid, df in timeseries.items():
        df = df.copy()
        df.insert(0, "basin_id", bid)

        if bid in attributes.index:
            for col in attributes.columns:
                df[col] = attributes.loc[bid, col]

        frames.append(df)

    combined = pd.concat(frames)

    if fmt == "parquet":
        combined.to_parquet(output)
    else:
        combined.to_csv(output)


def export_geometries(
    gdf: gpd.GeoDataFrame,
    output: Path,
    fmt: GeoFormat = "gpkg",
) -> None:
    """Export catchment geometries to GeoPackage or GeoJSON.

    Parameters
    ----------
    gdf:
        GeoDataFrame with catchment geometries.
    output:
        Output file path.
    fmt:
        Output format — "gpkg" for GeoPackage, "geojson" for GeoJSON.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    driver = "GPKG" if fmt == "gpkg" else "GeoJSON"
    logger.debug("Exporting geometries as %s to %s", fmt, output)
    gdf.to_file(output, driver=driver)
