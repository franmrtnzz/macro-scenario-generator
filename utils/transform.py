"""Data transformation helpers for external macro series."""

from __future__ import annotations

import pandas as pd


def normalize_series(df: pd.DataFrame, var_name: str | None = None, *, minmax: bool = False) -> pd.DataFrame:
    """Return a monthly DataFrame with columns date, variable and value.

    The previous implementation always min-max scaled values. That is useful for
    toy charts but harmful for macro interpretation, so raw units are preserved
    by default.
    """

    if "value" not in df.columns:
        raise ValueError("Input DataFrame must contain a 'value' column.")

    clean = df.copy()
    if "date" in clean.columns:
        clean["date"] = pd.to_datetime(clean["date"], errors="coerce")
        clean = clean.set_index("date")
    else:
        clean.index = pd.to_datetime(clean.index, errors="coerce")

    clean = clean[["value"]].sort_index()
    clean["value"] = pd.to_numeric(clean["value"], errors="coerce")
    clean = clean[~clean.index.isna()]
    clean = clean.resample("MS").mean().ffill()

    if minmax:
        min_val = clean["value"].min()
        max_val = clean["value"].max()
        if max_val == min_val:
            raise ValueError("Cannot min-max scale a constant series.")
        clean["value"] = (clean["value"] - min_val) / (max_val - min_val)

    out = clean.reset_index().rename(columns={"index": "date"})
    out["variable"] = var_name or "series"
    return out[["date", "variable", "value"]]
