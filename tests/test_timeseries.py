"""Tests for time series loading."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from camelsch.timeseries import (
    list_basins,
    list_variables,
    load_basin_timeseries,
    load_timeseries,
    resample_annual,
)


def test_list_basins(data_dir: Path, basin_ids: list[str]) -> None:
    """list_basins returns all fixture basin IDs."""
    result = list_basins(data_dir)
    assert sorted(result) == sorted(basin_ids)


def test_list_variables(data_dir: Path) -> None:
    """list_variables returns expected variable names."""
    variables = list_variables(data_dir)
    assert "discharge_spec" in variables
    assert "precipitation" in variables
    assert "pet_sim" in variables
    assert "et_sim" in variables
    # Aliases should be excluded from canonical list
    assert "pet" not in variables
    assert "et" not in variables


def test_load_basin_timeseries_single(data_dir: Path) -> None:
    """Load a single basin and check structure."""
    df = load_basin_timeseries(data_dir, "2004")
    assert isinstance(df, pd.DataFrame)
    assert isinstance(df.index, pd.DatetimeIndex)
    assert len(df) == 5  # 5 days of fixture data
    # Obs columns
    assert "discharge_spec" in df.columns
    assert "precipitation" in df.columns
    # Sim columns
    assert "pet_sim" in df.columns
    assert "et_sim" in df.columns
    # Aliases
    assert "pet" in df.columns
    assert "et" in df.columns


def test_load_basin_timeseries_strips_units(data_dir: Path) -> None:
    """Unit suffixes are stripped from column names."""
    df = load_basin_timeseries(data_dir, "2004")
    assert not any("(" in c for c in df.columns)


def test_load_basin_timeseries_no_gauge_id_column(data_dir: Path) -> None:
    """gauge_id column is dropped from per-basin time series."""
    df = load_basin_timeseries(data_dir, "2004")
    assert "gauge_id" not in df.columns


def test_load_timeseries_all(data_dir: Path, basin_ids: list[str]) -> None:
    """load_timeseries with no basin filter loads all basins."""
    result = load_timeseries(data_dir)
    assert sorted(result.keys()) == sorted(basin_ids)


def test_load_timeseries_filter_basins(data_dir: Path) -> None:
    """load_timeseries with basin filter loads only requested basins."""
    result = load_timeseries(data_dir, basin_ids=["2004", "3001"])
    assert sorted(result.keys()) == ["2004", "3001"]


def test_load_timeseries_filter_variables(data_dir: Path) -> None:
    """load_timeseries with variable filter includes only requested columns."""
    result = load_timeseries(
        data_dir,
        basin_ids=["2004"],
        variables=["precipitation", "discharge_spec"],
    )
    df = result["2004"]
    assert list(df.columns) == ["precipitation", "discharge_spec"]


def test_load_timeseries_filter_dates(data_dir: Path) -> None:
    """load_timeseries with date range filters rows."""
    result = load_timeseries(
        data_dir,
        basin_ids=["2004"],
        start_date="1981-01-02",
        end_date="1981-01-04",
    )
    df = result["2004"]
    assert len(df) == 3
    assert str(df.index.min().date()) == "1981-01-02"
    assert str(df.index.max().date()) == "1981-01-04"


def test_load_basin_not_found(data_dir: Path) -> None:
    """Loading a nonexistent basin raises FileNotFoundError."""
    import pytest

    with pytest.raises(FileNotFoundError):
        load_basin_timeseries(data_dir, "9999")


def test_load_timeseries_unknown_variables_returns_empty_columns(data_dir: Path) -> None:
    """Requesting only nonexistent variables returns DataFrame with 0 columns."""
    result = load_timeseries(data_dir, basin_ids=["2004"], variables=["nonexistent"])
    df = result["2004"]
    assert df.columns.tolist() == []
    assert len(df) == 5  # rows preserved


def test_load_timeseries_partial_variable_match(data_dir: Path) -> None:
    """Requesting a mix of valid and invalid variables returns only the valid ones."""
    result = load_timeseries(
        data_dir,
        basin_ids=["2004"],
        variables=["precipitation", "nonexistent"],
    )
    df = result["2004"]
    assert list(df.columns) == ["precipitation"]
    assert len(df) == 5


def test_resample_annual_sum_vs_mean() -> None:
    """resample_annual sums precipitation and averages temperature."""
    dates = pd.date_range("2020-01-01", periods=365, freq="D")
    df = pd.DataFrame(
        {
            "precipitation": [2.0] * 365,
            "temperature_mean": [10.0] * 365,
            "discharge_spec": [1.0] * 365,
        },
        index=dates,
    )
    result = resample_annual(df)
    assert len(result) == 1
    # precipitation and discharge should be summed
    assert result["precipitation"].iloc[0] == 365 * 2.0
    assert result["discharge_spec"].iloc[0] == 365 * 1.0
    # temperature should be averaged
    assert result["temperature_mean"].iloc[0] == 10.0
