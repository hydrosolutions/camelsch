# Changelog

## 0.1.0

Initial release.

- Download CAMELS-CH dataset from Zenodo (`camelsch download`)
- Show dataset summary (`camelsch info`)
- List basin IDs with optional attributes (`camelsch basins`)
- Extract static catchment attributes (`camelsch attributes`)
- Extract time series with variable/date filtering (`camelsch timeseries`)
- Batch export to CSV/Parquet with optional attribute merge (`camelsch export`)
- Python API: `load_attributes`, `load_timeseries`, `export_merged`, and more
- Handles Latin-1 encoding, unit-suffixed columns, and comment lines
