"""Tests for the CLI commands via typer.testing.CliRunner."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from camelsch.cli import app

runner = CliRunner()

FIXTURE_DIR = str(Path(__file__).parent / "fixtures" / "camels_ch")


def test_version_flag() -> None:
    """--version prints version and exits."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "camelsch" in result.output
    assert "0.1.0" in result.output


def test_info_missing_data_suggests_download() -> None:
    """info on a nonexistent dir suggests running 'camelsch download'."""
    result = runner.invoke(app, ["info", "--data-dir", "/tmp/nonexistent_camelsch"])
    assert result.exit_code != 0
    assert "camelsch download" in result.output


def test_info(data_dir: Path) -> None:
    """info command shows dataset summary."""
    result = runner.invoke(app, ["info", "--data-dir", str(data_dir)])
    assert result.exit_code == 0
    assert "Basins" in result.output
    assert "3" in result.output


def test_basins_table(data_dir: Path) -> None:
    """basins command in table format lists basin IDs."""
    result = runner.invoke(app, ["basins", "--data-dir", str(data_dir)])
    assert result.exit_code == 0
    assert "2004" in result.output
    assert "2007" in result.output
    assert "3001" in result.output


def test_basins_csv(data_dir: Path) -> None:
    """basins --format csv outputs one basin per line."""
    result = runner.invoke(app, ["basins", "--data-dir", str(data_dir), "--format", "csv"])
    assert result.exit_code == 0
    lines = [ln for ln in result.output.strip().splitlines() if ln.strip()]
    assert "2004" in lines
    assert "3001" in lines


def test_basins_json(data_dir: Path) -> None:
    """basins --format json outputs a JSON array of basin IDs."""
    import json

    result = runner.invoke(app, ["basins", "--data-dir", str(data_dir), "--format", "json"])
    assert result.exit_code == 0
    ids = json.loads(result.output)
    assert isinstance(ids, list)
    assert "2004" in ids


def test_attributes_stdout(data_dir: Path) -> None:
    """attributes command prints CSV to stdout when no --output."""
    result = runner.invoke(
        app, ["attributes", "--data-dir", str(data_dir), "--basins", "2004,2007"]
    )
    assert result.exit_code == 0
    assert "gauge_id" in result.output or "2004" in result.output


def test_attributes_to_file(data_dir: Path, tmp_path: Path) -> None:
    """attributes command writes CSV file when --output is given."""
    out = tmp_path / "attrs.csv"
    result = runner.invoke(
        app,
        ["attributes", "--data-dir", str(data_dir), "--output", str(out)],
    )
    assert result.exit_code == 0
    assert out.exists()
    content = out.read_text()
    assert "2004" in content


def test_timeseries_stdout(data_dir: Path) -> None:
    """timeseries command without --basins loads all basins."""
    result = runner.invoke(
        app,
        [
            "timeseries",
            "--data-dir",
            str(data_dir),
            "--vars",
            "precipitation",
        ],
    )
    assert result.exit_code == 0
    assert "precipitation" in result.output


def test_timeseries_to_file(data_dir: Path, tmp_path: Path) -> None:
    """timeseries command writes a file when --output is given."""
    out = tmp_path / "ts.csv"
    result = runner.invoke(
        app,
        [
            "timeseries",
            "--data-dir",
            str(data_dir),
            "--basins",
            "2004",
            "--output",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert out.exists()


def test_export_parquet(data_dir: Path, tmp_path: Path) -> None:
    """export command writes a parquet file."""
    out = tmp_path / "export.parquet"
    result = runner.invoke(
        app,
        [
            "export",
            "--data-dir",
            str(data_dir),
            "--basins",
            "2004",
            "--output",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert out.exists()


def test_export_csv(data_dir: Path, tmp_path: Path) -> None:
    """export command writes CSV when format is csv."""
    out = tmp_path / "export.csv"
    result = runner.invoke(
        app,
        [
            "export",
            "--data-dir",
            str(data_dir),
            "--basins",
            "2004",
            "--output",
            str(out),
            "--format",
            "csv",
        ],
    )
    assert result.exit_code == 0
    assert out.exists()


def test_export_with_attrs(data_dir: Path, tmp_path: Path) -> None:
    """export --include-attrs merges static attributes."""
    out = tmp_path / "merged.parquet"
    result = runner.invoke(
        app,
        [
            "export",
            "--data-dir",
            str(data_dir),
            "--basins",
            "2004",
            "--include-attrs",
            "--output",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert out.exists()


def test_download_skip_existing(data_dir: Path) -> None:
    """download command exits cleanly when data already exists at dest."""
    result = runner.invoke(app, ["download", "--dest", str(data_dir)])
    assert result.exit_code == 0
    assert "ready" in result.output.lower()
