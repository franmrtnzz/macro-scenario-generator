"""Optional ETL pipeline for refreshing external macro data."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import pandas as pd

from api.ecb import get_series_ecb
from api.fred import get_series_fred
from utils.io import save_series
from utils.transform import normalize_series


VARIABLES: dict[str, dict[str, Any]] = {
    "real_gdp_usa": {"source": "FRED", "id": "GDPC1"},
    "hicp_ea": {"source": "ECB", "dataset": "ICP", "key": "M.U2.N.000000.4.INX"},
    "policy_rate": {"source": "FRED", "id": "ECBDFR"},
    "long_rate": {"source": "FRED", "id": "IRLTLT01EZM156N"},
}


def run_etl_pipeline(vars_cfg: dict[str, dict[str, Any]] | None = None) -> dict[str, pd.DataFrame]:
    """Download and persist configured series without executing on import."""

    vars_cfg = vars_cfg or VARIABLES
    outputs: dict[str, pd.DataFrame] = {}
    for name, cfg in vars_cfg.items():
        raw = _download_series(cfg)
        normalized = normalize_series(raw, name)
        save_series(normalized, name)
        outputs[name] = normalized
    return outputs


def build_series_dataset(data_dir: str | Path = "data") -> dict[str, pd.Series]:
    """Build a unified series dictionary from previously saved ETL files."""

    data_dir = Path(data_dir)
    gdp = _load_saved_series(data_dir / "real_gdp_usa.pkl", "gdp")
    inflation = _load_saved_series(data_dir / "hicp_ea.pkl", "inflation")
    policy_rate = _load_saved_series(data_dir / "policy_rate.pkl", "policy_rate")
    long_rate = _load_saved_series(data_dir / "long_rate.pkl", "long_rate")

    aligned = pd.concat([policy_rate, long_rate, inflation], axis=1).dropna()
    spread = (aligned["long_rate"] - aligned["policy_rate"]).rename("spread")
    real_rate = (aligned["policy_rate"] - aligned["inflation"]).rename("real_rate")

    series = {
        "gdp": gdp,
        "inflation": inflation,
        "policy_rate": policy_rate,
        "long_rate": long_rate,
        "spread": spread,
        "real_rate": real_rate,
    }

    with (data_dir / "series.pkl").open("wb") as handle:
        pickle.dump(series, handle)
    return series


def _download_series(cfg: dict[str, Any]) -> pd.DataFrame:
    source = str(cfg["source"]).upper()
    if source == "FRED":
        return get_series_fred(str(cfg["id"]))
    if source == "ECB":
        return get_series_ecb(str(cfg["dataset"]), str(cfg["key"]))
    raise ValueError(f"Unknown data source: {cfg['source']}")


def _load_saved_series(path: Path, name: str) -> pd.Series:
    if not path.exists():
        raise FileNotFoundError(f"Missing ETL output: {path}")

    obj = pd.read_pickle(path)
    if isinstance(obj, pd.Series):
        series = obj.copy()
    elif isinstance(obj, pd.DataFrame):
        if "date" not in obj.columns or "value" not in obj.columns:
            raise ValueError(f"{path} must contain date and value columns.")
        series = obj.assign(date=pd.to_datetime(obj["date"], errors="coerce")).set_index("date")["value"]
    else:
        raise TypeError(f"Unsupported object in {path}: {type(obj).__name__}")

    series = pd.to_numeric(series, errors="coerce").sort_index()
    series.index = pd.to_datetime(series.index, errors="coerce")
    series = series[~series.index.isna()].resample("MS").mean().ffill()
    series.name = name
    return series


if __name__ == "__main__":
    run_etl_pipeline()
    build_series_dataset()
