"""Tests for attribute loading."""

from __future__ import annotations

from pathlib import Path

from camelsch.attributes import get_attribute_names, load_attributes


def test_load_attributes_returns_all_basins(data_dir: Path, basin_ids: list[str]) -> None:
    """load_attributes loads all 3 fixture basins."""
    df = load_attributes(data_dir)
    assert len(df) == 3
    assert sorted(df.index.tolist()) == sorted(basin_ids)


def test_load_attributes_merges_columns(data_dir: Path) -> None:
    """Attributes from all CSV files are merged into one DataFrame."""
    df = load_attributes(data_dir)
    # Topographic attrs
    assert "gauge_name" in df.columns
    assert "area" in df.columns
    # Climate attrs
    assert "p_mean" in df.columns
    # Supplement attrs
    assert "forest_frac" in df.columns
    # Simulation-based attrs
    assert "runoff_ratio_sim" in df.columns


def test_load_attributes_strips_units(data_dir: Path) -> None:
    """Unit suffixes are stripped from column names."""
    df = load_attributes(data_dir)
    # Original column was "area(km2)" -> "area"
    assert "area" in df.columns
    assert not any("(" in c for c in df.columns)


def test_load_attributes_filter_basins(data_dir: Path) -> None:
    """load_attributes can filter to specific basin IDs."""
    df = load_attributes(data_dir, basin_ids=["2004", "3001"])
    assert len(df) == 2
    assert "2004" in df.index
    assert "3001" in df.index
    assert "2007" not in df.index


def test_load_attributes_handles_latin1(data_dir: Path) -> None:
    """Topographic attributes file is Latin-1 encoded and should load fine."""
    df = load_attributes(data_dir)
    # gauge_name for 2004 contains "Zürich" which needs Latin-1
    name = df.loc["2004", "gauge_name"]
    assert "zürich" in name.lower()


def test_get_attribute_names(data_dir: Path) -> None:
    """get_attribute_names returns list of column names."""
    names = get_attribute_names(data_dir)
    assert isinstance(names, list)
    assert len(names) > 0
    assert "area" in names
