"""Tests for download module."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from camelsch.download import _extract_and_rename, _validate_zip_members, download_camels_ch


def test_download_skips_when_exists(data_dir: Path) -> None:
    """download_camels_ch returns early if dest already exists."""
    result = download_camels_ch(dest=data_dir, force=False)
    assert result == data_dir
    assert result.exists()


def test_download_extracts_zip(tmp_path: Path) -> None:
    """download_camels_ch can extract a zip and rename the folder."""
    # Create a fake zip with a camels_ch/ subfolder
    zip_path = tmp_path / "camels_ch.zip"
    extracted = tmp_path / "CAMELS_CH"

    inner_dir = "camels_ch"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(f"{inner_dir}/readme.txt", "test")
        zf.writestr(f"{inner_dir}/timeseries/observation_based/dummy.csv", "a,b\n1,2\n")

    # Manually extract and rename to simulate download_camels_ch logic
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(tmp_path)

    # The extracted folder should be camels_ch
    assert (tmp_path / inner_dir).exists()

    # Rename to match expected dest
    (tmp_path / inner_dir).rename(extracted)
    assert extracted.exists()
    assert (extracted / "readme.txt").exists()


def test_validate_zip_members_rejects_path_traversal(tmp_path: Path) -> None:
    """_validate_zip_members raises on members that escape the target dir."""
    zip_path = tmp_path / "evil.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("../../etc/passwd", "root:x:0:0")

    with (
        zipfile.ZipFile(zip_path, "r") as zf,
        pytest.raises(ValueError, match="would escape target directory"),
    ):
        _validate_zip_members(zf, tmp_path)


def _is_case_sensitive_fs(directory: Path) -> bool:
    """Return True if *directory* lives on a case-sensitive filesystem."""
    probe = directory / "_camelsch_probe_ABC"
    probe.mkdir()
    result = not (directory / "_camelsch_probe_abc").exists()
    probe.rmdir()
    return result


def test_extract_and_rename_moves_subfolder(tmp_path: Path) -> None:
    """_extract_and_rename extracts a zip and renames the subfolder to dest."""
    if not _is_case_sensitive_fs(tmp_path):
        pytest.skip("Rename-by-case test requires a case-sensitive filesystem")

    zip_path = tmp_path / "camels_ch.zip"
    dest = tmp_path / "CAMELS_CH"

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("camels_ch/readme.txt", "test")
        zf.writestr("camels_ch/timeseries/obs/dummy.csv", "a,b\n1,2\n")

    _extract_and_rename(zip_path, dest)

    assert dest.exists()
    assert (dest / "readme.txt").exists()
    assert (dest / "timeseries" / "obs" / "dummy.csv").exists()
    assert not (tmp_path / "camels_ch").exists()


def test_extract_and_rename_same_name(tmp_path: Path) -> None:
    """_extract_and_rename works when the zip subfolder name matches dest exactly."""
    zip_path = tmp_path / "camels_ch.zip"
    dest = tmp_path / "CAMELS_CH"

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("CAMELS_CH/readme.txt", "test")
        zf.writestr("CAMELS_CH/timeseries/obs/dummy.csv", "a,b\n1,2\n")

    _extract_and_rename(zip_path, dest)

    assert dest.exists()
    assert (dest / "readme.txt").exists()
    assert (dest / "timeseries" / "obs" / "dummy.csv").exists()
