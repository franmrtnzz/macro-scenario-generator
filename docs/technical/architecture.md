# Technical Architecture

## Current Design

The application is organised around a deterministic scenario engine and a static browser dashboard.

1. The user selects or edits shocks in `web/index.html`.
2. `web/terminal.js` builds the scenario, charts, exports and market ticker in the browser.
3. The dashboard renders paths, deltas, diagnostics and exports.
4. `quant/macro_engine.py` remains the Python reference implementation.
5. Tests verify that the reference engine keeps coherent behaviour.

## Why The Engine Is Semi-Structural

The previous VAR workflow depended on a fragile data pickle, scale transformations and random noise injection. The rebuilt engine prioritises:

- interpretability,
- stable deterministic behaviour,
- transparent assumptions,
- user-facing units,
- and clear communication of limitations.

This makes the product more defensible as a scenario tool, even though it is less statistically ambitious than a fitted econometric model.

## Core Modules

`quant/macro_engine.py`

- Defines baseline assumptions.
- Defines shock channels and presets.
- Applies response profiles over a chosen horizon.
- Produces baseline, scenario and delta columns.
- Runs coherence checks and regime classification.

`quant/narrative.py`

- Generates deterministic analyst notes.
- Summarises transmission, policy interpretation and risk flags.
- Produces Markdown reports for export.

`web/`

- Provides scenario setup, shock editing, visualisation and export.
- Uses Plotly.js for baseline-vs-scenario and delta charts.
- Includes a horizontal market ticker with structured mock data, isolated behind `renderStockTicker(items)` for later API integration.
- Runs without a Python backend.

`etl/pipeline.py`

- Optional helper for refreshing external macro series.
- Does not execute downloads on import.

## Output Contract

Scenario results include:

- `*_baseline`: baseline path.
- `*_scenario`: shocked path.
- `*_delta`: scenario deviation from baseline.

Variables:

- `gdp_growth`
- `inflation`
- `policy_rate`
- `real_rate`
- `output_gap`
