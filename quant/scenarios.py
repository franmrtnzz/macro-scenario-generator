# quant/scenarios.py
import os
import pickle
import pandas as pd

from quant.var_model import train_var_model, simulate_var_shock
from quant.input_validation import validate_shocks


def _ensure_monthly_index(series_dict):
    """
    Convierte índices no‐fecha en DatetimeIndex mensual (inicio de mes).
    """
    fixed = {}
    for name, s in series_dict.items():
        if not isinstance(s.index, pd.DatetimeIndex):
            new_idx = pd.date_range(
                end=pd.Timestamp.today(), periods=len(s), freq="MS"  # ← cambio aquí
            )
            s = s.copy()
            s.index = new_idx
        fixed[name] = s
    return fixed


def simulate_scenario(shocks_dict, scenario_name="var_run", steps=12):
    # 1. Cargar series históricas
    with open("data/series.pkl", "rb") as f:
        series_dict = pickle.load(f)

    # 2. Asegurar índice mensual
    series_dict = _ensure_monthly_index(series_dict)

    # 3. Validar shocks
    latest_date = max(cfg["start"] for cfg in shocks_dict.values())
    full_range = pd.date_range(
        start=series_dict["gdp"].index.min(),
        end=pd.to_datetime(latest_date) + pd.offsets.MonthEnd(0),
        freq="MS"
    )
    validate_shocks(shocks_dict, [d.strftime("%Y-%m") for d in full_range])

    # 4. Entrenar VAR
    print("🧠 Entrenando modelo VAR...")
    var_model = train_var_model(series_dict)

    # 5. Simular con shocks
    print("📈 Simulando escenario con shocks...")
    simulated_df = simulate_var_shock(var_model, shocks_dict, steps)

    # 6. Guardar resultado
    os.makedirs("data/scenarios", exist_ok=True)
    with open(f"data/scenarios/{scenario_name}.pkl", "wb") as f:
        pickle.dump(simulated_df, f)

    print(f"✅ Escenario '{scenario_name}' simulado y guardado correctamente.")
    return simulated_df


# ── Ejecución directa de prueba ────────────────────────────────
if __name__ == "__main__":
    shocks = {
    "gdp": {"shock_type": "increase", "value": 0.015, "start": "2024-06"},
    "inflation": {"shock_type": "decrease", "value": 0.01, "start": "2024-07"}
}

    simulate_scenario(shocks, scenario_name="var_run")
