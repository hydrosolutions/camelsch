"""camelsch — CLI tool for CAMELS-CH hydrological data extraction."""

import logging

from camelsch.attributes import get_attribute_names, load_attributes
from camelsch.download import download_camels_ch
from camelsch.export import export_attributes, export_geometries, export_merged, export_timeseries
from camelsch.geometries import load_geometries
from camelsch.timeseries import (
    list_basins,
    list_variables,
    load_basin_timeseries,
    load_timeseries,
    resample_annual,
)

__version__ = "0.2.0"

logging.getLogger(__name__).addHandler(logging.NullHandler())

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
