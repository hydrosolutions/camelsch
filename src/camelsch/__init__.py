"""camelsch — CLI tool for CAMELS-CH hydrological data extraction."""

import logging
from typing import TYPE_CHECKING

from camelsch.attributes import get_attribute_names, load_attributes
from camelsch.download import download_camels_ch
from camelsch.export import export_attributes, export_merged, export_timeseries
from camelsch.timeseries import (
    list_basins,
    list_variables,
    load_basin_timeseries,
    load_timeseries,
    resample_annual,
)

if TYPE_CHECKING:
    from camelsch.export import export_geometries as export_geometries
    from camelsch.geometries import load_geometries as load_geometries

__version__ = "0.3.0"

logging.getLogger(__name__).addHandler(logging.NullHandler())

_LAZY_IMPORTS = {
    "export_geometries": ("camelsch.export", "export_geometries"),
    "load_geometries": ("camelsch.geometries", "load_geometries"),
}

__all__ = [
    "download_camels_ch",
    "export_attributes",
    "export_geometries",
    "export_merged",
    "export_timeseries",
    "get_attribute_names",
    "list_basins",
    "list_variables",
    "load_attributes",
    "load_basin_timeseries",
    "load_geometries",
    "load_timeseries",
    "resample_annual",
]


def __getattr__(name: str) -> object:
    if name in _LAZY_IMPORTS:
        module_path, attr = _LAZY_IMPORTS[name]
        import importlib

        mod = importlib.import_module(module_path)
        val = getattr(mod, attr)
        globals()[name] = val  # cache for subsequent access
        return val
    raise AttributeError(f"module 'camelsch' has no attribute {name!r}")


def __dir__() -> list[str]:
    return [*list(__all__), "__version__"]
