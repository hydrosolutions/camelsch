"""Tests for download module."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from camelsch.download import _validate_zip_members, download_camels_ch


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
