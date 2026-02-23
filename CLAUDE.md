# CLAUDE.md — camelsch

## Project overview
camelsch is a CLI tool for downloading, exploring, and extracting data from the CAMELS-CH hydrological dataset (331 Swiss basins, 1981–2020).

## Repository layout
- `src/camelsch/` — package source (Python API + CLI)
  - `cli.py` — Typer CLI entry point (6 commands)
  - `download.py` — Download & extraction logic
  - `io.py` — Shared CSV reading helpers (encoding fallback, unit stripping)
  - `attributes.py` — Static catchment attributes
  - `timeseries.py` — Time series loading & querying
  - `export.py` — Export to CSV/Parquet
- `tests/` — pytest tests
- `tests/fixtures/` — small synthetic CSVs mimicking CAMELS-CH format
- `tests/create_fixtures.py` — script to regenerate fixture files

## Build & run
- Package manager: **uv** (use `uv run`, `uv add`, `uv sync`)
- Linting: **ruff** (`uv run ruff check src/ tests/`)
- Formatting: **ruff** (`uv run ruff format src/ tests/`)
- Tests: `uv run pytest` (or `uv run pytest -x` for fail-fast)
- Run CLI: `uv run camelsch <command>`

## CLI commands
- `camelsch download` — Download CAMELS-CH from Zenodo
- `camelsch info` — Show dataset summary
- `camelsch basins` — List basin IDs (table/csv/json)
- `camelsch attributes` — Extract static attributes
- `camelsch timeseries` — Extract time series with filtering
- `camelsch export` — Batch export merged data

## Key conventions
- Python 3.10+, type hints throughout, `py.typed` marker present
- CLI built with **typer** (entry point: `camelsch.cli:app`)
- Source layout: `src/camelsch/`
- All commands accept `--data-dir` (or `CAMELSCH_DATA_DIR` env var, default `./data/CAMELS_CH`)

## Data format quirks (critical)
- Column names include units in parentheses — strip with `re.sub(r"\(.*?\)\s*$", "", name)`
- Encoding is Latin-1 (ISO-8859-1), not UTF-8 — `io.read_csv_robust()` handles fallback
- Attribute CSVs have `#` comment lines — use `comment="#"` in `pd.read_csv()`
- Basin ID column is `gauge_id` (4-digit FOEN identifiers)
- Date column is `date` (lowercase), format `YYYY-MM-DD`
- Obs + sim time series are separate files per basin — merge on date index
- Aliases: `pet_sim` → `pet`, `et_sim` → `et`

## Testing
- Fixtures are synthetic CSVs in `tests/fixtures/camels_ch/` (regenerate with `uv run python tests/create_fixtures.py`)
- Tests cover: unit stripping, encoding fallback, obs+sim merge, variable/date filtering, export formats
- 24 tests across 4 test files
