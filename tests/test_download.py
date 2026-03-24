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
    """_extract_and_rename extracts a zip with a subfolder to dest."""
    zip_path = tmp_path / "camels_ch.zip"
    dest = tmp_path / "CAMELS_CH"

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("camels_ch/readme.txt", "test")
        zf.writestr("camels_ch/timeseries/observation_based/dummy.csv", "a,b\n1,2\n")

    _extract_and_rename(zip_path, dest)

    assert dest.exists()
    assert (dest / "readme.txt").exists()
    assert (dest / "timeseries" / "observation_based" / "dummy.csv").exists()


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


def test_extract_and_rename_moves_subfolder(tmp_path: Path) -> None:
    """_extract_and_rename extracts a zip and moves the subfolder to dest."""
    zip_path = tmp_path / "camels_ch.zip"
    dest = tmp_path / "CAMELS_CH"

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("camels_ch/readme.txt", "test")
        zf.writestr("camels_ch/timeseries/obs/dummy.csv", "a,b\n1,2\n")

    _extract_and_rename(zip_path, dest)

    assert dest.exists()
    assert (dest / "readme.txt").exists()
    assert (dest / "timeseries" / "obs" / "dummy.csv").exists()


def test_extract_and_rename_same_name(tmp_path: Path) -> None:
    """_extract_and_rename works when the zip subfolder name matches dest."""
    zip_path = tmp_path / "camels_ch.zip"
    dest = tmp_path / "CAMELS_CH"

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("CAMELS_CH/readme.txt", "test")
        zf.writestr("CAMELS_CH/timeseries/obs/dummy.csv", "a,b\n1,2\n")

    _extract_and_rename(zip_path, dest)

    assert dest.exists()
    assert (dest / "readme.txt").exists()
    assert (dest / "timeseries" / "obs" / "dummy.csv").exists()


def test_extract_and_rename_no_camels_folder_raises(tmp_path: Path) -> None:
    """_extract_and_rename raises FileNotFoundError when zip has no camels folder."""
    zip_path = tmp_path / "bad.zip"
    dest = tmp_path / "CAMELS_CH"

    with zipfile.ZipFile(zip_path, "w"):
        pass  # Empty zip

    with pytest.raises(FileNotFoundError, match="Could not find extracted"):
        _extract_and_rename(zip_path, dest)
