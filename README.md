# camelsch

[![CI](https://github.com/hydrosolutions/camelsch/actions/workflows/ci.yml/badge.svg)](https://github.com/hydrosolutions/camelsch/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13-blue)](https://www.python.org)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/hydrosolutions/camelsch/HEAD?labpath=demo.ipynb)

CLI tool for downloading, exploring, and extracting data from the [CAMELS-CH](https://zenodo.org/records/15025258) hydrological dataset (331 Swiss basins, 1981-2020).

## Maintenance Status

🟢 **Active** – Maintained by [hydrosolutions](https://github.com/hydrosolutions)

---

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

CAMELS-CH provides daily hydrometeorological time series and static catchment attributes for 331 Swiss basins (1981-2020). The dataset contains 21 time series variables:

**Observation-based (9 variables)**

| Variable | Description |
|---|---|
| `discharge_vol` | Discharge volume (m³/s) |
| `discharge_spec` | Specific discharge (mm/d) |
| `waterlevel` | Water level (m) |
| `precipitation` | Basin-mean daily precipitation (mm/d) |
| `temperature_min` | Minimum daily temperature (°C) |
| `temperature_mean` | Mean daily temperature (°C) |
| `temperature_max` | Maximum daily temperature (°C) |
| `rel_sun_dur` | Relative sunshine duration (%) |
| `swe` | Snow water equivalent (mm) |

**Simulation-based (12 variables)**

| Variable | Description |
|---|---|
| `discharge_vol_sim` | Simulated discharge volume (m³/s) |
| `discharge_spec_sim` | Simulated specific discharge (mm/d) |
| `precipitation_sim` | Simulated precipitation (mm/d) |
| `temperature_sim` | Simulated temperature (°C) |
| `radiation_sim` | Simulated radiation (W/m²) |
| `sun_duration_sim` | Simulated sunshine duration (h) |
| `wind_sim` | Simulated wind speed (m/s) |
| `rel_humidity_sim` | Simulated relative humidity (%) |
| `pet_sim` | Simulated potential evapotranspiration (mm/d) |
| `et_sim` | Simulated actual evapotranspiration (mm/d) |
| `intercept_et_sim` | Simulated interception evapotranspiration (mm/d) |
| `intercept_storage_sim` | Simulated interception storage (mm) |

Convenience aliases: `pet` → `pet_sim`, `et` → `et_sim`.

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
