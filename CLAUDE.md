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

### Orchestration Protocol

**CRITICAL: The orchestrator (you) must NEVER write implementation code directly. All code changes are delegated to Sonnet 4.6 general-purpose agents.**

**Responsibilities:**

1. **Explore** — Before each phase, read relevant files and gather context. Build agent prompts that include specific file paths, function signatures, and the exact scope of allowed changes.

2. **Constrain** — Every agent prompt MUST include:
   - The list of files the agent is allowed to modify
   - An explicit instruction: *"Do NOT change any existing function signatures, data flow logic, or control flow. Your changes must be purely additive or modify only the specific behavior described."*
   - The expected behavior before and after the change

3. **Delegate** — Launch Sonnet 4.6 general-purpose agents for all implementation. Use `isolation: "worktree"` for changes that carry risk of unintended side effects. Run independent phases in parallel; run dependent phases sequentially.

4. **Deliberate** — After each agent returns, before accepting its work:
   - Review the diff: does it touch only the files and functions that were scoped?
   - Check for unintended changes: renamed variables, reordered imports, reformatted code, altered logic paths
   - Verify the change preserves existing data flow by tracing inputs → outputs through the modified code
   - If anything is out of scope or unclear, reject and re-delegate with tighter constraints

5. **Verify** — Run `SAPPHIRE_TEST_ENV=True bash run_tests.sh` after each phase. Zero failures, zero unexpected skips.

6. **Iterate** — If tests fail or review finds issues, delegate targeted fixes to a new agent. Never patch over problems in the orchestrator.

7. **Commit** — Only when all tests pass and deliberation is complete.

**Plan structure:** Plans must be organized into phases with explicit dependencies. Each phase specifies:
- **Goal**: What this phase accomplishes
- **Files**: Which files may be modified
- **Depends on**: Which prior phases must complete first
- **Agents**: How many parallel agents, what each one does
- **Acceptance criteria**: How to verify the phase succeeded

End the plan with a dependency graph:

```json
{
  "phases": {
    "P1": { "depends_on": [], "parallel_agents": 2 },
    "P2": { "depends_on": ["P1"], "parallel_agents": 1 },
    "P3": { "depends_on": ["P1"], "parallel_agents": 1 },
    "P4": { "depends_on": ["P2", "P3"], "parallel_agents": 1 }
  }
}
```