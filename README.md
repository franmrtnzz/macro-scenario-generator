# Macro Scenario Generator

A Streamlit application for running macroeconomic scenario simulations with vector autoregression (VAR) models.

The project focuses on transparent scenario mechanics: loading macroeconomic time series, configuring shocks, simulating paths, visualizing results, and exporting outputs for further analysis.

## Features

- VAR model training for selected macroeconomic variables.
- Shock simulation with configurable magnitude, horizon, persistence, and decay.
- ECB and FRED data ingestion utilities.
- Streamlit interface for scenario configuration and review.
- CSV export for simulation outputs.
- Optional narrative summary generation when an OpenAI API key is available.

## Architecture

```text
macro-scenario-generator/
  api/                  ECB and FRED API clients
  etl/                  data preparation pipeline
  quant/                VAR model, input validation, and shock propagation
  scripts/              narrative and maintenance scripts
  utils/                export and transformation helpers
  docs/                 technical notes and user guide
  tests/                pytest suite
  streamlit_app.py      Streamlit entry point
```

The quantitative layer is separated from the Streamlit interface so model logic can be tested without the web application.

## Technology

- Python
- pandas and NumPy
- statsmodels
- scikit-learn
- Streamlit
- Plotly and Matplotlib
- pytest

## Local Setup

```bash
git clone https://github.com/franmrtnzz/macro-scenario-generator.git
cd macro-scenario-generator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

On Windows, activate the virtual environment with `venv\Scripts\activate`.

## Configuration

Create a `.env` file only if you want narrative summaries:

```env
OPENAI_API_KEY=
```

The core VAR simulation and visualization workflow does not require this key.

## Testing

```bash
python -m pytest tests/
```

The tests cover API normalization, data processing, model training, and simulation helpers.

## Notes

This is an applied modelling tool, not a forecasting product. VAR outputs depend heavily on variable selection, transformations, lag specification, and the historical sample. Results should be read as scenario mechanics rather than point forecasts.
