"""Load and merge observation + simulation time series."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from camelsch.io import extract_basin_id, find_date_column, read_csv_robust, strip_units

logger = logging.getLogger(__name__)


def _read_ts_csv(path: Path) -> pd.DataFrame:
    """Read a single time series CSV with encoding fallback and unit stripping."""
    df = read_csv_robust(path)
    df.columns = [strip_units(c) for c in df.columns]

    date_col = find_date_column(df)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], format="%Y-%m-%d")
        if date_col != "date":
            df = df.rename(columns={date_col: "date"})
        df = df.set_index("date")

    # Drop gauge_id column from data — it's redundant in per-basin files
    if "gauge_id" in df.columns:
        df = df.drop(columns=["gauge_id"])

    return df


def _add_aliases(df: pd.DataFrame) -> pd.DataFrame:
    """Add convenience aliases: pet_sim -> pet, et_sim -> et."""
    if "pet_sim" in df.columns and "pet" not in df.columns:
        df["pet"] = df["pet_sim"]
    if "et_sim" in df.columns and "et" not in df.columns:
        df["et"] = df["et_sim"]
    return df


def _find_timeseries_dirs(data_dir: Path) -> tuple[Path | None, Path | None]:
    """Find observation_based/ and simulation_based/ directories."""
    ts_dir = data_dir / "timeseries"
    obs_dir = ts_dir / "observation_based"
    sim_dir = ts_dir / "simulation_based"
    return (
        obs_dir if obs_dir.exists() else None,
        sim_dir if sim_dir.exists() else None,
    )


def list_basins(data_dir: str | Path) -> list[str]:
    """List all available basin IDs from time series filenames."""
    data_dir = Path(data_dir)
    obs_dir, sim_dir = _find_timeseries_dirs(data_dir)

    ids: set[str] = set()
    for d in (obs_dir, sim_dir):
        if d is not None:
            for f in d.glob("*.csv"):
                ids.add(extract_basin_id(f))
    return sorted(ids)


def list_variables(data_dir: str | Path) -> list[str]:
    """List all available variable names from a sample basin."""
    data_dir = Path(data_dir)
    basin_ids = list_basins(data_dir)
    if not basin_ids:
        return []
    sample = load_basin_timeseries(data_dir, basin_ids[0])
    # Exclude aliases from the canonical list
    return [c for c in sample.columns if c not in ("pet", "et")]


def load_basin_timeseries(data_dir: str | Path, basin_id: str) -> pd.DataFrame:
    """Load and merge obs + sim time series for one basin.

    Args:
        data_dir: Path to the extracted ``camels_ch`` directory.
        basin_id: 4-digit FOEN gauge identifier (e.g. ``"2004"``).

    Returns:
        DataFrame with DatetimeIndex and all observation + simulation columns.
    """
    data_dir = Path(data_dir)
    obs_dir, sim_dir = _find_timeseries_dirs(data_dir)

    obs: pd.DataFrame | None = None
    sim: pd.DataFrame | None = None

    if obs_dir:
        matches = list(obs_dir.glob(f"*_{basin_id}.csv"))
        if matches:
            if len(matches) > 1:
                logger.warning(
                    "Multiple files match basin %s in %s, using %s",
                    basin_id,
                    obs_dir,
                    matches[0].name,
                )
            obs = _read_ts_csv(matches[0])

    if sim_dir:
        matches = list(sim_dir.glob(f"*_{basin_id}.csv"))
        if matches:
            if len(matches) > 1:
                logger.warning(
                    "Multiple files match basin %s in %s, using %s",
                    basin_id,
                    sim_dir,
                    matches[0].name,
                )
            sim = _read_ts_csv(matches[0])

    if obs is None and sim is None:
        msg = f"No time series files found for basin {basin_id}"
        raise FileNotFoundError(msg)

    if obs is not None and sim is not None:
        merged = obs.join(sim, how="outer")
        logger.debug("Merged obs+sim for basin %s (%d rows)", basin_id, len(merged))
    elif obs is not None:
        merged = obs
    else:
        merged = sim  # both-None handled above

    assert merged is not None
    return _add_aliases(merged)


def load_timeseries(
    data_dir: str | Path,
    basin_ids: list[str] | None = None,
    variables: list[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, pd.DataFrame]:
    """Load time series for multiple basins with optional filtering.

    Args:
        data_dir: Path to the extracted ``camels_ch`` directory.
        basin_ids: List of basin IDs to load. If ``None``, loads all.
        variables: Variables to include. If ``None``, includes all.
        start_date: Start date filter (YYYY-MM-DD).
        end_date: End date filter (YYYY-MM-DD).

    Returns:
        Dict mapping basin ID to its merged time series DataFrame.
    """
    data_dir = Path(data_dir)

    if basin_ids is None:
        basin_ids = list_basins(data_dir)
        if not basin_ids:
            msg = f"No time series files found in {data_dir / 'timeseries'}"
            raise FileNotFoundError(msg)

    result: dict[str, pd.DataFrame] = {}
    for bid in basin_ids:
        df = load_basin_timeseries(data_dir, bid)

        if start_date:
            df = df.loc[start_date:]  # type: ignore[misc]
        if end_date:
            df = df.loc[:end_date]  # type: ignore[misc]
        if variables:
            cols = [v for v in variables if v in df.columns]
            missing = [v for v in variables if v not in df.columns]
            if missing:
                logger.warning("Variables not found in basin %s: %s", bid, ", ".join(missing))
            df = df[cols]

        result[bid] = df

    return result


_SUM_PATTERNS: tuple[str, ...] = (
    "precipitation",
    "discharge",
    "swe",
    "intercept_et",
    "intercept_storage",
)


def resample_annual(df: pd.DataFrame) -> pd.DataFrame:
    """Resample daily time series to annual resolution.

    Uses sum for precipitation, discharge, and SWE columns; mean for all
    others (temperature, radiation, humidity, PET, ET, etc.).

    The input must have a DatetimeIndex.

    Parameters
    ----------
    df:
        Daily time series DataFrame with DatetimeIndex.

    Returns
    -------
    pd.DataFrame
        Annual time series.
    """
    agg: dict[str, str] = {}
    for col in df.columns:
        col_lower = col.lower()
        if any(pat in col_lower for pat in _SUM_PATTERNS):
            agg[col] = "sum"
        else:
            agg[col] = "mean"
    try:
        return df.resample("YE").agg(agg)  # type: ignore[arg-type]
    except ValueError:
        return df.resample("A").agg(agg)  # type: ignore[arg-type]
