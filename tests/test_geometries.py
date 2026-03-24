"""Tests for geometry loading functionality."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pytest

from camelsch.geometries import load_geometries


def test_load_geometries_returns_geodataframe(data_dir: Path) -> None:
    """load_geometries returns a GeoDataFrame with all 3 basins."""
    gdf = load_geometries(data_dir)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert len(gdf) == 3


def test_load_geometries_index_is_gauge_id(data_dir: Path) -> None:
    """Index is gauge_id with string values."""
    gdf = load_geometries(data_dir)
    assert gdf.index.name == "gauge_id"
    assert set(gdf.index) == {"2004", "2007", "3001"}


def test_load_geometries_native_crs(data_dir: Path) -> None:
    """Default CRS is EPSG:2056 (LV95)."""
    gdf = load_geometries(data_dir)
    assert gdf.crs is not None
    assert gdf.crs.to_epsg() == 2056


def test_load_geometries_reproject(data_dir: Path) -> None:
    """Passing crs reprojects the geometries."""
    gdf = load_geometries(data_dir, crs="EPSG:4326")
    assert gdf.crs is not None
    assert gdf.crs.to_epsg() == 4326


def test_load_geometries_filter_basins(data_dir: Path) -> None:
    """Passing basin_ids filters to those basins only."""
    gdf = load_geometries(data_dir, basin_ids=["2004"])
    assert len(gdf) == 1
    assert "2004" in gdf.index


def test_load_geometries_missing_dir_raises(tmp_path: Path) -> None:
    """Raises FileNotFoundError when catchment_delineations is missing."""
    with pytest.raises(FileNotFoundError):
        load_geometries(tmp_path)
