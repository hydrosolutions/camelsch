"""Shared test fixtures for camelsch tests."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "camels_ch"


@pytest.fixture()
def data_dir() -> Path:
    """Return path to the synthetic CAMELS-CH fixture directory."""
    return FIXTURE_DIR


@pytest.fixture()
def basin_ids() -> list[str]:
    """Return the basin IDs present in the fixture data."""
    return ["2004", "2007", "3001"]
