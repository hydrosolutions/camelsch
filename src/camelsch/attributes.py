"""Load and merge static attribute CSVs."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from camelsch.io import find_id_column, read_csv_robust, strip_units

logger = logging.getLogger(__name__)


def _read_attribute_csv(path: Path) -> pd.DataFrame:
    """Read a single CAMELS-CH attribute CSV handling encoding and comments."""
    df = read_csv_robust(path)
    df.columns = [strip_units(c) for c in df.columns]

    id_col = find_id_column(df)
    if id_col:
        df[id_col] = df[id_col].astype(str)
        if id_col != "gauge_id":
            df = df.rename(columns={id_col: "gauge_id"})
        df = df.set_index("gauge_id")

    return df


def load_attributes(
    data_dir: str | Path,
    basin_ids: list[str] | None = None,
) -> pd.DataFrame:
    """Load and merge all static attribute CSVs.

    Reads every ``*.csv`` under ``static_attributes/`` (including subdirectories),
    strips unit suffixes from column names, and merges on ``gauge_id``.

    Args:
        data_dir: Path to the extracted ``camels_ch`` directory.
        basin_ids: Optional list of basin IDs to filter to.

    Returns:
        DataFrame indexed by ``gauge_id`` with all attribute columns.
    """
    data_dir = Path(data_dir)
    attr_dir = data_dir / "static_attributes"

    csv_files = sorted(attr_dir.glob("*.csv"))
    for subdir in ["supplements", "simulation_based"]:
        sub = attr_dir / subdir
        if sub.exists():
            csv_files.extend(sorted(sub.glob("*.csv")))

    if not csv_files:
        msg = f"No attribute CSVs found in {attr_dir}"
        raise FileNotFoundError(msg)

    merged: pd.DataFrame | None = None
    for csv_path in csv_files:
        df = _read_attribute_csv(csv_path)
        logger.debug("Loaded attribute file %s (%d cols)", csv_path.name, len(df.columns))
        if merged is None:
            merged = df
        else:
            dropped = [c for c in df.columns if c in merged.columns]
            if dropped:
                logger.warning(
                    "Duplicate columns in %s (skipped): %s",
                    csv_path.name,
                    ", ".join(dropped),
                )
            new_cols = [c for c in df.columns if c not in merged.columns]
            if new_cols:
                merged = merged.join(df[new_cols], how="outer")

    if merged is None:
        msg = f"No attribute data could be loaded from {attr_dir}"
        raise ValueError(msg)

    if basin_ids is not None:
        merged = merged.loc[merged.index.isin(basin_ids)]

    logger.debug("Attributes loaded: %d basins, %d columns", len(merged), len(merged.columns))
    return merged


def get_attribute_names(data_dir: str | Path) -> list[str]:
    """List all available attribute column names."""
    df = load_attributes(data_dir)
    return list(df.columns)
