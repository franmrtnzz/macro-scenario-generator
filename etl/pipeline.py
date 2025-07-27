# etl/pipeline.py
from typing import Dict
import os
import pickle
import pandas as pd

from api.fred import get_series_fred
from api.ecb import get_series_ecb
from utils.transform import normalize_series
from utils.io import save_series

# ────────────────────────────────────────────────────────────────
# 1️⃣ Variables a procesar
# ────────────────────────────────────────────────────────────────
VARIABLES: Dict[str, Dict] = {
    "real_gdp_usa": {"source": "FRED", "id": "GDPC1"},
    "hicp_ea":      {"source": "ECB",  "dataset": "ICP", "key": "M.U2.N.000000.4.INX"},
    "policy_rate":  {"source": "FRED", "id": "ECBDFR"},
    "long_rate":    {"source": "FRED", "id": "IRLTLT01EZM156N"},
}

# ────────────────────────────────────────────────────────────────
# 2️⃣ Helper: asegurar que cada objeto es Series con nombre fijo
# ────────────────────────────────────────────────────────────────
def ensure_series(obj, name: str) -> pd.Series:
    """Convierte DataFrame o Series a Series con índice datetime y nombre correcto."""
    if isinstance(obj, pd.DataFrame):
        if "value" in obj.columns:
            obj = obj["value"]
        else:
            obj = obj.iloc[:, 0]
    obj = obj.astype(float)
    obj.index = pd.to_datetime(obj.index)
    obj.name = name
    return obj

# ────────────────────────────────────────────────────────────────
# 3️⃣ Ejecutar ETL (descargar → normalizar → guardar)
# ────────────────────────────────────────────────────────────────
def run_etl_pipeline(vars_cfg: Dict[str, Dict]) -> None:
    for name, cfg in vars_cfg.items():
        print(f"\n🔄 Procesando {name} ...")
        if cfg["source"].upper() == "FRED":
            df_raw = get_series_fred(cfg["id"])
        elif cfg["source"].upper() == "ECB":
            df_raw = get_series_ecb(cfg["dataset"], cfg["key"])
        else:
            print(f"⚠️  Fuente desconocida: {cfg['source']} → omito")
            continue
        df_norm = normalize_series(df_raw, name)
        save_series(df_norm, name)

run_etl_pipeline(VARIABLES)

# ────────────────────────────────────────────────────────────────
# 4️⃣ Cargar series individuales como Series limpias
# ────────────────────────────────────────────────────────────────
with open("data/real_gdp_usa.pkl", "rb") as f:
    gdp_df = pickle.load(f)
gdp_series = (
    gdp_df.set_index("date")["value"].astype(float)
)
gdp_series.index = pd.to_datetime(gdp_series.index)
gdp_series.name = "gdp"

with open("data/hicp_ea.pkl", "rb") as f:
    inflation_series = ensure_series(pickle.load(f), "inflation")

with open("data/policy_rate.pkl", "rb") as f:
    policy_rate_series = ensure_series(pickle.load(f), "policy_rate")

with open("data/long_rate.pkl", "rb") as f:
    long_rate_series = ensure_series(pickle.load(f), "long_rate")

# ────────────────────────────────────────────────────────────────
# 5️⃣ Series derivadas: spread y real_rate
# ────────────────────────────────────────────────────────────────
aligned = pd.concat(
    [policy_rate_series, long_rate_series, inflation_series],
    axis=1
).dropna()

spread_series    = (aligned["long_rate"] - aligned["policy_rate"]).rename("spread")
real_rate_series = (aligned["policy_rate"] - aligned["inflation"]).rename("real_rate")

# ────────────────────────────────────────────────────────────────
# 6️⃣ Diccionario final y guardado
# ────────────────────────────────────────────────────────────────
series_dict = {
    "gdp":         gdp_series,
    "inflation":   inflation_series,
    "policy_rate": policy_rate_series,
    "long_rate":   long_rate_series,
    "spread":      spread_series,
    "real_rate":   real_rate_series,
}

os.makedirs("data", exist_ok=True)
with open("data/series.pkl", "wb") as f:
    pickle.dump(series_dict, f)

print("✅ Archivo unificado series.pkl guardado con: gdp, inflation, policy_rate, long_rate, spread, real_rate")
