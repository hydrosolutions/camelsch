"""CLI entry point for camelsch."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from camelsch import __version__

Format = Literal["csv", "parquet"]
GeoFormat = Literal["gpkg", "geojson"]

app = typer.Typer(
    name="camelsch",
    help="CLI tool for CAMELS-CH hydrological data extraction.",
    no_args_is_help=True,
)

DEFAULT_DATA_DIR = Path("./data/CAMELS_CH")

console = Console()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"camelsch {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """CLI tool for CAMELS-CH hydrological data extraction."""


def resolve_data_dir(data_dir: Path | None) -> Path:
    """Resolve data directory from argument, env var, or default."""
    if data_dir is not None:
        return data_dir
    env = os.environ.get("CAMELSCH_DATA_DIR")
    if env:
        return Path(env)
    return DEFAULT_DATA_DIR


def _check_data_dir(dd: Path) -> None:
    """Exit with a friendly hint if the data directory doesn't exist."""
    if not dd.exists():
        console.print(f"[red]Directory not found: {dd}[/red]")
        console.print("Run 'camelsch download' first.")
        raise typer.Exit(1)


def _infer_format(output: Path, fmt: str) -> Format:
    """Infer output format from file extension, falling back to *fmt*."""
    if output.suffix == ".parquet":
        return "parquet"
    if output.suffix == ".csv":
        return "csv"
    if fmt in ("csv", "parquet"):
        return fmt  # type: ignore[return-value]
    return "csv"


def _infer_geo_format(output: Path, fmt: str) -> GeoFormat:
    """Infer geometry output format from file extension, falling back to *fmt*."""
    if output.suffix == ".geojson":
        return "geojson"
    if output.suffix == ".gpkg":
        return "gpkg"
    if fmt == "geojson":
        return "geojson"
    return "gpkg"


# ---------------------------------------------------------------------------
# download
# ---------------------------------------------------------------------------


@app.command()
def download(
    dest: Path = typer.Option(DEFAULT_DATA_DIR, help="Target directory."),
    force: bool = typer.Option(False, help="Re-download even if exists."),
    url: str | None = typer.Option(None, help="Custom Zenodo URL to download from."),
) -> None:
    """Download and extract the CAMELS-CH dataset from Zenodo.

    Example: camelsch download --dest ./my_data
    """
    from camelsch.download import download_camels_ch

    kwargs: dict[str, object] = {"dest": dest, "force": force}
    if url is not None:
        kwargs["url"] = url
    path = download_camels_ch(**kwargs)  # type: ignore[arg-type]
    console.print(f"[green]Dataset ready at {path}[/green]")


# ---------------------------------------------------------------------------
# info
# ---------------------------------------------------------------------------


@app.command()
def info(
    data_dir: Path | None = typer.Option(None, help="Path to CAMELS_CH dir."),
) -> None:
    """Show dataset summary: basins, time range, variables.

    Example: camelsch info --data-dir ./data/CAMELS_CH
    """
    from camelsch.attributes import load_attributes
    from camelsch.timeseries import (
        list_basins,
        list_variables,
        load_basin_timeseries,
    )

    dd = resolve_data_dir(data_dir)
    _check_data_dir(dd)

    basin_ids = list_basins(dd)
    variables = list_variables(dd)

    date_range = ""
    if basin_ids:
        sample = load_basin_timeseries(dd, basin_ids[0])
        if len(sample.index) > 0:
            date_range = f"{sample.index.min().date()} to {sample.index.max().date()}"

    try:
        attrs = load_attributes(dd)
        attr_count = len(attrs.columns)
    except FileNotFoundError:
        attr_count = 0

    geom_dir = dd / "catchment_delineations"
    geom_status = "Available (LV95 / EPSG:2056)" if geom_dir.exists() else "Not found"

    table = Table(title="CAMELS-CH Dataset Summary", show_header=False)
    table.add_column("Key", style="bold")
    table.add_column("Value")
    table.add_row("Location", str(dd))
    table.add_row("Basins", str(len(basin_ids)))
    table.add_row("Time range", date_range)
    table.add_row("Variables", ", ".join(variables))
    table.add_row("Attributes", f"{attr_count} static features")
    table.add_row("Geometry", geom_status)
    console.print(table)


# ---------------------------------------------------------------------------
# basins
# ---------------------------------------------------------------------------


@app.command()
def basins(
    data_dir: Path | None = typer.Option(None, help="Path to CAMELS_CH dir."),
    fmt: str = typer.Option("table", "--format", help="Output: table, csv, json."),
    attrs: str | None = typer.Option(None, help="Comma-separated attribute names."),
) -> None:
    """List available basin IDs with optional attributes.

    Example: camelsch basins --format json --attrs area,p_mean
    """
    from camelsch.timeseries import list_basins as _list_basins

    dd = resolve_data_dir(data_dir)
    _check_data_dir(dd)
    basin_ids = _list_basins(dd)

    attr_df = None
    if attrs:
        from camelsch.attributes import load_attributes

        attr_names = [a.strip() for a in attrs.split(",")]
        attr_df = load_attributes(dd)
        valid_cols = [c for c in attr_names if c in attr_df.columns]
        attr_df = attr_df[valid_cols] if valid_cols else attr_df.iloc[:, :0]
        attr_df = attr_df.loc[attr_df.index.isin(basin_ids)]

    if fmt == "json":
        _basins_json(basin_ids, attr_df)
    elif fmt == "csv":
        _basins_csv(basin_ids, attr_df)
    else:
        _basins_table(basin_ids, attr_df)


def _basins_json(basin_ids: list[str], attr_df: pd.DataFrame | None) -> None:
    """Output basin list as JSON."""
    if attr_df is not None:
        records = []
        for bid in basin_ids:
            rec: dict[str, object] = {"basin_id": bid}
            if bid in attr_df.index:
                rec.update(attr_df.loc[bid].to_dict())  # type: ignore[arg-type]
            records.append(rec)
        typer.echo(json.dumps(records, indent=2))
    else:
        typer.echo(json.dumps(basin_ids, indent=2))


def _basins_csv(basin_ids: list[str], attr_df: pd.DataFrame | None) -> None:
    """Output basin list as CSV."""
    if attr_df is not None:
        header = "basin_id," + ",".join(attr_df.columns)
        typer.echo(header)
        for bid in basin_ids:
            if bid in attr_df.index:
                vals = ",".join(str(v) for v in attr_df.loc[bid])
                typer.echo(f"{bid},{vals}")
            else:
                typer.echo(bid)
    else:
        for bid in basin_ids:
            typer.echo(bid)


def _basins_table(basin_ids: list[str], attr_df: pd.DataFrame | None) -> None:
    """Output basin list as a rich table."""
    table = Table(title="CAMELS-CH Basins")
    table.add_column("basin_id")
    if attr_df is not None:
        for col in attr_df.columns:
            table.add_column(col)
        for bid in basin_ids:
            if bid in attr_df.index:
                row = attr_df.loc[bid]
                table.add_row(bid, *(str(v) for v in row))
            else:
                table.add_row(bid, *[""] * len(attr_df.columns))
    else:
        for bid in basin_ids:
            table.add_row(bid)
    console.print(table)


# ---------------------------------------------------------------------------
# attributes
# ---------------------------------------------------------------------------


@app.command()
def attributes(
    data_dir: Path | None = typer.Option(None, help="Path to CAMELS_CH dir."),
    basins_opt: str | None = typer.Option(None, "--basins", help="Comma-separated basin IDs."),
    output: Path | None = typer.Option(None, help="Output file path."),
    fmt: str = typer.Option("csv", "--format", help="Output format: csv or parquet."),
) -> None:
    """Extract static catchment attributes to CSV or Parquet.

    Example: camelsch attributes --basins 2004,2007 --output attrs.csv
    """
    from camelsch.attributes import load_attributes
    from camelsch.export import export_attributes

    dd = resolve_data_dir(data_dir)
    _check_data_dir(dd)
    bid_list = [b.strip() for b in basins_opt.split(",")] if basins_opt else None
    df = load_attributes(dd, basin_ids=bid_list)

    if output:
        export_attributes(df, output, fmt=_infer_format(output, fmt))
        console.print(f"[green]Attributes written to {output}[/green]")
    else:
        typer.echo(df.to_csv())


# ---------------------------------------------------------------------------
# timeseries
# ---------------------------------------------------------------------------


@app.command()
def timeseries(
    data_dir: Path | None = typer.Option(None, help="Path to CAMELS_CH dir."),
    basins_opt: str | None = typer.Option(
        None, "--basins", help="Comma-separated basin IDs, or 'all'."
    ),
    vars_opt: str | None = typer.Option(None, "--vars", help="Comma-separated variable names."),
    start: str | None = typer.Option(None, help="Start date (YYYY-MM-DD)."),
    end: str | None = typer.Option(None, help="End date (YYYY-MM-DD)."),
    output: Path | None = typer.Option(None, help="Output file path."),
    fmt: str = typer.Option("csv", "--format", help="Output format: csv or parquet."),
    resolution: str = typer.Option(
        "daily", "--resolution", help="Temporal resolution: daily or annual."
    ),
) -> None:
    """Extract time series data for one or more basins.

    Example: camelsch timeseries --basins 2004 --vars precipitation --start 1990-01-01
    """
    from camelsch.export import export_timeseries
    from camelsch.timeseries import load_timeseries

    dd = resolve_data_dir(data_dir)
    _check_data_dir(dd)
    bid_list = (
        None
        if basins_opt is None or basins_opt.strip().lower() == "all"
        else [b.strip() for b in basins_opt.split(",")]
    )
    var_list = [v.strip() for v in vars_opt.split(",")] if vars_opt else None

    data = load_timeseries(
        dd,
        basin_ids=bid_list,
        variables=var_list,
        start_date=start,
        end_date=end,
    )

    if resolution == "annual":
        from camelsch.timeseries import resample_annual

        data = {bid: resample_annual(df) for bid, df in data.items()}

    if output:
        export_timeseries(data, output, fmt=_infer_format(output, fmt))
        console.print(f"[green]Time series written to {output}[/green]")
    else:
        for bid, df in data.items():
            if len(data) > 1:
                typer.echo(f"--- Basin {bid} ---")
            typer.echo(df.to_csv())


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------


@app.command()
def export(
    data_dir: Path | None = typer.Option(None, help="Path to CAMELS_CH dir."),
    basins_opt: str | None = typer.Option(None, "--basins", help="Comma-separated basin IDs."),
    output: Path = typer.Option(Path("camels_ch_export.parquet"), help="Output file path."),
    fmt: str = typer.Option("parquet", "--format", help="Output format: csv or parquet."),
    include_attrs: bool = typer.Option(False, help="Merge static attributes into output."),
    include_geometry: bool = typer.Option(
        False, "--include-geometry", help="Export catchment geometries."
    ),
    crs: str | None = typer.Option(
        None, "--crs", help="Reproject geometries to CRS (e.g. EPSG:4326)."
    ),
) -> None:
    """Batch export: merge time series (+ optional attributes) into one file.

    Example: camelsch export --basins 2004,2007 --include-attrs --output merged.parquet
    """
    from camelsch.attributes import load_attributes
    from camelsch.export import export_merged, export_timeseries
    from camelsch.timeseries import load_timeseries

    dd = resolve_data_dir(data_dir)
    _check_data_dir(dd)
    bid_list = [b.strip() for b in basins_opt.split(",")] if basins_opt else None

    data = load_timeseries(dd, basin_ids=bid_list)

    resolved_fmt = _infer_format(output, fmt)

    if include_attrs:
        attrs = load_attributes(dd, basin_ids=bid_list)
        export_merged(data, attrs, output, fmt=resolved_fmt)
    else:
        export_timeseries(data, output, fmt=resolved_fmt)

    if include_geometry:
        from camelsch.export import export_geometries
        from camelsch.geometries import load_geometries

        gdf = load_geometries(dd, basin_ids=bid_list, crs=crs)
        geo_fmt = _infer_geo_format(output, fmt)
        geo_suffix = ".geojson" if geo_fmt == "geojson" else ".gpkg"
        geo_output = output.with_name(output.stem + "_geometry" + geo_suffix)
        export_geometries(gdf, geo_output, fmt=geo_fmt)
        console.print(f"[green]Geometries written to {geo_output}[/green]")
    elif crs is not None:
        console.print("[yellow]--crs ignored without --include-geometry[/yellow]")

    console.print(f"[green]Exported {len(data)} basin(s) to {output}[/green]")
