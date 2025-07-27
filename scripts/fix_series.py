# scripts/fix_series.py

import pickle
import pandas as pd

# 1. Cargar el series.pkl actual
with open("data/series.pkl", "rb") as f:
    series = pickle.load(f)

# 2. Transformar la serie de inflación si está en formato plano
inflation = series.get("inflation")

# Verificamos si necesita transformación
if isinstance(inflation, pd.DataFrame) and {"date", "value"}.issubset(inflation.columns):
    print("🔧 Transformando inflación...")
    inflation["date"] = pd.to_datetime(inflation["date"])
    inflation.set_index("date", inplace=True)
    inflation_series = inflation["value"]  # Nos quedamos solo con la columna de valores
    series["inflation"] = inflation_series
else:
    print("✅ La serie de inflación ya está en formato correcto")

# 3. Guardar el nuevo series.pkl
with open("data/series.pkl", "wb") as f:
    pickle.dump(series, f)

print("✅ Archivo series.pkl actualizado correctamente")
