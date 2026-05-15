# Macro Scenario Generator

Macro Scenario Generator is a browser-based macroeconomic scenario lab for exploring how shocks propagate through growth, inflation, policy rates, real rates and the output gap.

The platform is now a custom static dashboard. That gives the product stronger visual control, faster public access and a cleaner deployment path: anyone with the published URL can open the platform directly in their browser.

## What It Does

- Builds baseline and shocked macro paths over 6-60 months.
- Supports demand, supply/energy, monetary policy, financial risk and fiscal shocks.
- Shows baseline vs scenario paths and deviations from baseline.
- Produces an analyst-style narrative with regime classification and coherence flags.
- Includes a Bloomberg/IBKR-style market ticker with structured mock assets ready to connect to a live market-data API.
- Exports scenario data and Markdown reports from the browser.

## Run Locally

```bash
python -m http.server 8000 -d web
```

Open:

```text
http://localhost:8000
```

## Python Validation

The Python modules remain as the reference engine and test layer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

## Architecture

```text
macro-scenario-generator/
|-- web/
|   |-- index.html          # Browser dashboard
|   |-- terminal.css        # Terminal/workstation product styling
|   `-- terminal.js         # Frontend scenario engine, charts and ticker
|-- quant/
|   |-- macro_engine.py     # Python reference scenario engine
|   `-- narrative.py        # Python narrative/report generation
|-- etl/
|   `-- pipeline.py         # Optional external data refresh helpers
|-- utils/
|-- input/
|-- examples/
|-- docs/
`-- tests/
```

## Deployment

The dashboard is static. Recommended options:

- GitHub Pages serving the `web/` folder.
- Netlify with publish directory `web`.
- Vercel configured as a static project with output directory `web`.
- Cloudflare Pages with build command empty and output directory `web`.

No backend, API key or database is required for the public platform.

A GitHub Pages workflow is included in `.github/workflows/pages.yml`. Configure Pages to use `GitHub Actions` as the source and the generated URL will be public after the deployment run succeeds.

## Model Summary

The engine uses calibrated response profiles for five shock channels:

- Demand: activity first, inflation and policy with lags.
- Supply / energy: inflation pressure plus weaker activity.
- Monetary policy: direct rate path, delayed demand and inflation effects.
- Financial risk: weaker activity, softer inflation and easier policy.
- Fiscal impulse: activity support with mild inflation and policy effects.

Outputs are reported in interpretable units:

- GDP growth: `% y/y`
- Inflation: `% y/y`
- Policy rate: `%`
- Real rate: `%`
- Output gap: `% potential GDP`

This is a scenario tool, not a point-forecasting system. It is designed for structured sensitivity analysis and communication, not for claims of econometric precision.

## Important Launch Reminder

When the final public URL is generated, update the platform links in:

- the LinkedIn publication,
- the website article.
