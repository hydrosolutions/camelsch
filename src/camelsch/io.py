"""Shared I/O helpers for reading CAMELS-CH CSV files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd


def strip_units(name: str) -> str:
    """Strip parenthesised unit suffixes from a column name.

    Examples:
        >>> strip_units("discharge_spec(mm/d)")
        'discharge_spec'
        >>> strip_units("temperature_mean(degC)")
        'temperature_mean'
        >>> strip_units("gauge_id")
        'gauge_id'
    """
    return re.sub(r"\(.*?\)\s*$", "", name).strip()


def read_csv_robust(filepath: Path, **kwargs: Any) -> pd.DataFrame:
    """Read CSV trying utf-8, then latin-1 encoding. Handle comment lines."""
    for encoding in ("utf-8", "latin-1"):
        try:
            df: pd.DataFrame = pd.read_csv(filepath, comment="#", encoding=encoding, **kwargs)
            return df
        except UnicodeDecodeError:
            continue
    msg = f"Could not decode {filepath} with utf-8 or latin-1"
    raise ValueError(msg)


def find_id_column(df: pd.DataFrame) -> str | None:
    """Detect basin/gauge ID column from common names.

    Examples:
        >>> import pandas as pd
        >>> find_id_column(pd.DataFrame({"gauge_id": [1], "value": [2]}))
        'gauge_id'
        >>> find_id_column(pd.DataFrame({"basin_id": [1], "value": [2]}))
        'basin_id'
        >>> find_id_column(pd.DataFrame({"x": [1], "y": [2]})) is None
        True
    """
    candidates = ["gauge_id", "basin_id", "id", "ID", "station_id", "catchment_id"]
    for name in candidates:
        if name in df.columns:
            return name
    return None


def find_date_column(df: pd.DataFrame) -> str | None:
    """Detect date/time column from common names.

    Examples:
        >>> import pandas as pd
        >>> find_date_column(pd.DataFrame({"date": ["2020-01-01"], "value": [1]}))
        'date'
        >>> find_date_column(pd.DataFrame({"timestamp": ["2020-01-01"]}))
        'timestamp'
        >>> find_date_column(pd.DataFrame({"x": [1]})) is None
        True
    """
    candidates = ["date", "Date", "datetime", "time", "timestamp"]
    for name in candidates:
        if name in df.columns:
            return name
    return None


def extract_basin_id(filepath: Path) -> str:
    """Extract numeric basin ID from filename.

    Expects filenames like ``CAMELS_CH_obs_based_2034.csv`` → ``"2034"``.

    Examples:
        >>> extract_basin_id(Path("CAMELS_CH_obs_based_2034.csv"))
        '2034'
        >>> extract_basin_id(Path("/data/timeseries/sim_2007.csv"))
        '2007'
    """
    return filepath.stem.rsplit("_", 1)[-1]
