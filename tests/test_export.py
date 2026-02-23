"""Tests for export functionality."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from camelsch.attributes import load_attributes
from camelsch.export import export_attributes, export_merged, export_timeseries
from camelsch.timeseries import load_timeseries


def test_export_timeseries_csv_single(data_dir: Path, tmp_path: Path) -> None:
    """Exporting one basin to CSV produces a single file."""
    data = load_timeseries(data_dir, basin_ids=["2004"])
    output = tmp_path / "ts.csv"
    export_timeseries(data, output, fmt="csv")
    assert output.exists()
    df = pd.read_csv(output, index_col=0, parse_dates=True)
    assert len(df) == 5


def test_export_timeseries_csv_multi(data_dir: Path, tmp_path: Path) -> None:
    """Exporting multiple basins to CSV produces a directory of files."""
    data = load_timeseries(data_dir, basin_ids=["2004", "2007"])
    output = tmp_path / "ts_dir"
    export_timeseries(data, output, fmt="csv")
    assert output.is_dir()
    assert (output / "basin_2004.csv").exists()
    assert (output / "basin_2007.csv").exists()


def test_export_timeseries_parquet(data_dir: Path, tmp_path: Path) -> None:
    """Exporting to parquet produces a single file with basin_id column."""
    data = load_timeseries(data_dir, basin_ids=["2004", "2007"])
    output = tmp_path / "ts.parquet"
    export_timeseries(data, output, fmt="parquet")
    assert output.exists()
    df = pd.read_parquet(output)
    assert "basin_id" in df.columns
    assert set(df["basin_id"].unique()) == {"2004", "2007"}


def test_export_attributes_csv(data_dir: Path, tmp_path: Path) -> None:
    """Exporting attributes to CSV."""
    attrs = load_attributes(data_dir)
    output = tmp_path / "attrs.csv"
    export_attributes(attrs, output, fmt="csv")
    assert output.exists()
    df = pd.read_csv(output, index_col=0)
    assert len(df) == 3


def test_export_attributes_parquet(data_dir: Path, tmp_path: Path) -> None:
    """Exporting attributes to parquet."""
    attrs = load_attributes(data_dir)
    output = tmp_path / "attrs.parquet"
    export_attributes(attrs, output, fmt="parquet")
    assert output.exists()
    df = pd.read_parquet(output)
    assert len(df) == 3


def test_export_merged(data_dir: Path, tmp_path: Path) -> None:
    """Exporting merged timeseries + attributes."""
    data = load_timeseries(data_dir, basin_ids=["2004"])
    attrs = load_attributes(data_dir)
    output = tmp_path / "merged.parquet"
    export_merged(data, attrs, output, fmt="parquet")
    assert output.exists()
    df = pd.read_parquet(output)
    assert "basin_id" in df.columns
    # Should have timeseries columns plus attribute columns
    assert "discharge_spec" in df.columns
    assert "area" in df.columns
