"""Geometry helpers for loading CAMELS-CH catchment shapefiles."""

from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd

from camelsch.io import find_id_column, strip_units

logger = logging.getLogger(__name__)


def _find_shapefile(data_dir: Path) -> Path:
    """Walk data_dir/catchment_delineations recursively for the first .shp file.

    Returns the path to the first shapefile found (sorted for determinism).

    Raises FileNotFoundError if the directory does not exist or contains no
    .shp files.
    """
    delineations_dir = data_dir / "catchment_delineations"
    if not delineations_dir.exists():
        raise FileNotFoundError(f"No shapefile found in {data_dir}/catchment_delineations/")
    matches = sorted(delineations_dir.rglob("*.shp"))
    if not matches:
        raise FileNotFoundError(f"No shapefile found in {data_dir}/catchment_delineations/")
    return matches[0]


def load_geometries(
    data_dir: str | Path,
    basin_ids: list[str] | None = None,
    crs: str | int | None = None,
) -> gpd.GeoDataFrame:
    """Load catchment geometries from the CAMELS-CH shapefile.

    Locates the shapefile under data_dir/catchment_delineations/, reads it
    into a GeoDataFrame, strips unit suffixes from column names, and sets the
    gauge ID column as the index.

    Parameters
    ----------
    data_dir:
        Root directory of the CAMELS-CH dataset.
    basin_ids:
        Optional list of basin IDs to keep. If None, all basins are returned.
    crs:
        Optional CRS to reproject to (e.g. "EPSG:4326" or 4326).

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame indexed by gauge ID (if the ID column is found).
    """
    data_dir = Path(data_dir)
    path = _find_shapefile(data_dir)
    logger.debug("Reading shapefile: %s", path)

    gdf = gpd.read_file(path)

    # Strip unit suffixes from all column names.
    gdf.columns = [strip_units(col) if col != gdf.geometry.name else col for col in gdf.columns]

    # Set gauge ID column as index.
    id_col = find_id_column(gdf)
    if id_col is not None:
        gdf[id_col] = gdf[id_col].astype(str)
        gdf = gdf.set_index(id_col)
    else:
        logger.warning("No gauge ID column found in shapefile %s; index will be positional.", path)

    # Filter to requested basins.
    if basin_ids is not None:
        gdf = gdf.loc[gdf.index.isin(basin_ids)]

    # Reproject if requested.
    if crs is not None:
        gdf = gdf.to_crs(crs)

    return gdf
