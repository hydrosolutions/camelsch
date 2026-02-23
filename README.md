# camelsch

[![CI](https://github.com/mabesa/camelsch/actions/workflows/ci.yml/badge.svg)](https://github.com/mabesa/camelsch/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13-blue)](https://www.python.org)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mabesa/camelsch/HEAD?labpath=demo.ipynb)

CLI tool for downloading, exploring, and extracting data from the [CAMELS-CH](https://zenodo.org/records/15025258) hydrological dataset (331 Swiss basins, 1981-2020).

## Installation

```bash
pip install camelsch
```

This also works inside conda/mamba environments — just activate yours first.

If you use [uv](https://docs.astral.sh/uv/) for project management:

```bash
uv add camelsch
```

## Workflow

camelsch follows a **download-then-query** workflow:

1. **Download** the CAMELS-CH dataset once from Zenodo (~1.5 GB).
2. **Explore** the dataset — list basins, check available variables, view summaries.
3. **Extract** the data you need — filter by basin, variable, and date range, then export to CSV or Parquet.

All commands read from a local data directory (default `./data/CAMELS_CH`). You can change it with `--data-dir` or the `CAMELSCH_DATA_DIR` environment variable.

## Quick start

```bash
# Step 1: Download the dataset from Zenodo (~1.5 GB)
camelsch download

# Step 2: Explore — show dataset summary
camelsch info

# List all basin IDs
camelsch basins
camelsch basins --format json
camelsch basins --format csv --attrs area,p_mean

# Step 3: Extract data
# Static catchment attributes
camelsch attributes --basins 2004,2007 --output attrs.csv

# Time series with filtering
camelsch timeseries --basins 2004 --vars precipitation,discharge_spec \
    --start 1990-01-01 --end 2000-12-31 --output ts.csv

# Batch export to Parquet (with optional attribute merge)
camelsch export --include-attrs --output camels_ch.parquet
```

## Python API

```python
import camelsch

# Load static attributes for specific basins
attrs = camelsch.load_attributes("./data/CAMELS_CH", basin_ids=["2004", "2007"])

# Load time series with filtering
data = camelsch.load_timeseries(
    "./data/CAMELS_CH",
    basin_ids=["2004"],
    variables=["precipitation", "discharge_spec"],
    start_date="1990-01-01",
    end_date="2000-12-31",
)

# List available basins and variables
basins = camelsch.list_basins("./data/CAMELS_CH")
variables = camelsch.list_variables("./data/CAMELS_CH")
```

## Data reference

CAMELS-CH provides daily hydrometeorological time series and static catchment attributes for 331 Swiss basins (1981-2020). Key variables include:

| Variable | Description |
|---|---|
| `precipitation` | Basin-mean daily precipitation (mm/d) |
| `temperature` | Basin-mean daily temperature (deg C) |
| `discharge_spec` | Observed specific discharge (mm/d) |
| `discharge_spec_sim` | Simulated specific discharge (mm/d) |
| `pet` / `pet_sim` | Potential evapotranspiration (mm/d) |
| `et` / `et_sim` | Actual evapotranspiration (mm/d) |
| `snow_water_eq_sim` | Simulated snow water equivalent (mm) |

Static attributes cover topography (`area`, `elev_mean`), climate (`p_mean`, `t_mean`), land cover, soil, and geology.

**Full dataset**: [CAMELS-CH on Zenodo](https://zenodo.org/records/15025258)
**Reference paper**: Hoege et al. (2023), *CAMELS-CH: hydro-meteorological time series and landscape attributes for 331 catchments in hydrologic Switzerland*, Earth Syst. Sci. Data.

## For developers

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Lint and format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type check
uv run mypy src/
```

## License

MIT
