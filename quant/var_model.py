# quant/var_model.py
import pickle
import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR
from sklearn.preprocessing import StandardScaler


# ────────────────────────────────────────────────────────────────
# Entrenamiento robusto del VAR
# ────────────────────────────────────────────────────────────────
def train_var_model(series_path: str, lags: int = 1, min_vars: int = 2, 
                   max_corr: float = 0.85, min_std: float = 0.0001):
    """
    Entrena un VAR robusto con:
      • gdp en primera diferencia (si es viable)
      • inflation, policy_rate, real_rate en nivel o diff según variabilidad
      • Filtrado inteligente de colinealidad usando rango de matriz
      • Escalado robusto y validación de singularidad
    """
    # 1. Cargar el pickle con las series
    with open(series_path, "rb") as f:
        raw = pickle.load(f)

    # 2. Limpieza rápida → Series mensuales (MS)
    clean = {}
    for name, obj in raw.items():
        s = obj.set_index("date")["value"] if isinstance(obj, pd.DataFrame) else obj
        idx = pd.to_datetime(s.index, errors="coerce").to_period("M").to_timestamp()
        s  = (
            s.set_axis(idx)
              .astype(float)
              .groupby(level=0).first()   # elimina duplicados
              .asfreq("MS")               # frecuencia mensual inicio
        )
        clean[name] = s

    df = pd.DataFrame(clean).ffill().loc["1970-01-01":]
    df = df[df.notna().sum(axis=1) >= 1]

    # 3. Análisis de variabilidad para decidir transformaciones
    print("🔍 Analizando variabilidad de series...")
    
    # Calcular std para cada serie en nivel y diff
    std_level = df.std()
    std_diff = df.diff().std()
    
    print(f"Std en nivel: {std_level.to_dict()}")
    print(f"Std en diff:  {std_diff.to_dict()}")
    
    # Decidir transformaciones basado en variabilidad
    df_transformed = pd.DataFrame(index=df.index)
    
    # gdp: usar diff si es viable, sino nivel
    if std_diff['gdp'] > min_std and not pd.isna(std_diff['gdp']):
        df_transformed['gdp'] = df['gdp'].diff()
        print("✅ gdp: usando diff")
    else:
        df_transformed['gdp'] = df['gdp']
        print("⚠️  gdp: usando nivel (diff no viable)")
    
    # Para las demás variables, usar la transformación con más variabilidad
    for var in ['inflation', 'policy_rate', 'real_rate']:
        if std_diff[var] > std_level[var] * 0.5:  # diff tiene al menos 50% de la varianza del nivel
            df_transformed[var] = df[var].diff()
            print(f"✅ {var}: usando diff (std_diff={std_diff[var]:.4f})")
        else:
            df_transformed[var] = df[var]
            print(f"✅ {var}: usando nivel (std_level={std_level[var]:.4f})")
    
    # 4. Limpiar NaN y verificar suficientes datos
    df_clean = df_transformed.dropna()
    
    if len(df_clean) < lags + 10:  # mínimo 10 observaciones + lags
        raise RuntimeError(f"Datos insuficientes tras limpieza: {len(df_clean)} filas")
    
    print(f"📏 Datos disponibles: {len(df_clean)} filas, {len(df_clean.columns)} columnas")
    
    # 5. Filtrado inteligente de colinealidad usando rango de matriz
    print("🔍 Analizando colinealidad...")
    
    # Calcular correlaciones
    corr_matrix = df_clean.corr().abs()
    print(f"Correlaciones máximas: {corr_matrix.max().max():.3f}")
    
    # Para variables constantes, añadir ruido pequeño para hacerlas viables
    for col in df_clean.columns:
        if df_clean[col].std() < 0.01:
            noise = np.random.normal(0, 0.001, len(df_clean))
            df_clean.loc[:, col] = df_clean[col] + noise
            print(f"🔧 Añadido ruido a {col} (std={df_clean[col].std():.6f})")
    
    # Eliminar variables con std muy baja (pero con umbral más permisivo)
    low_std_cols = df_clean.std()[df_clean.std() < min_std].index
    if len(low_std_cols) > 0:
        print(f"⚠️  Eliminando columnas con std < {min_std}: {list(low_std_cols)}")
        df_clean = df_clean.drop(columns=list(low_std_cols))
    
    # Si quedan muy pocas variables, ser más agresivo
    if len(df_clean.columns) < 3:
        print(f"⚠️  Pocas variables ({len(df_clean.columns)}), siendo más agresivo...")
        # Añadir más ruido a variables constantes
        for col in df_clean.columns:
            if df_clean[col].std() < 0.01:
                noise = np.random.normal(0, 0.01, len(df_clean))  # más ruido
                df_clean.loc[:, col] = df_clean[col] + noise
                print(f"🔧 Añadido más ruido a {col} (std={df_clean[col].std():.6f})")
    
    # Eliminar variables muy correlacionadas usando rango de matriz
    remaining_cols = list(df_clean.columns)
    final_cols = []
    
    for col in remaining_cols:
        test_cols = final_cols + [col]
        test_data = df_clean[test_cols]
        
        # Calcular rango de la matriz de correlaciones
        corr_test = test_data.corr()
        rank = np.linalg.matrix_rank(corr_test)
        
        if rank == len(test_cols):  # matriz de rango completo
            final_cols.append(col)
            print(f"✅ Añadida: {col}")
        else:
            print(f"❌ Rechazada: {col} (colinealidad)")
    
    if len(final_cols) < min_vars:
        raise RuntimeError(f"Variables insuficientes tras filtrado: {len(final_cols)} < {min_vars}")
    
    df_final = df_clean[final_cols]
    print(f"🎯 Variables finales: {final_cols}")
    
    # 6. Escalado robusto
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(
        scaler.fit_transform(df_final),
        index=df_final.index,
        columns=df_final.columns
    )
    
    # 7. Verificación final de singularidad
    X = df_scaled.values
    rank_X = np.linalg.matrix_rank(X)
    print(f"📊 Rango de matriz de datos: {rank_X}/{X.shape[1]}")
    
    if rank_X < X.shape[1]:
        raise RuntimeError("Matriz de datos singular - problema de colinealidad persistente")
    
    # 8. Ajustar VAR con trend='n' para evitar problemas de constante
    print("🚀 Entrenando VAR...")
    model = VAR(df_scaled)
    
    try:
        results = model.fit(lags, trend='n')  # sin constante
        print("✅ VAR entrenado exitosamente sin constante")
    except:
        # Si falla, intentar con constante
        print("⚠️  Reintentando con constante...")
        results = model.fit(lags, trend='c')
        print("✅ VAR entrenado exitosamente con constante")
    
    print(f"📈 Modelo final: VAR({lags}) con {len(final_cols)} variables")
    return results


# ────────────────────────────────────────────────────────────────
# Simulación de shocks
# ────────────────────────────────────────────────────────────────
def simulate_var_shock(results, shocks_dict: dict, steps: int = 12) -> pd.DataFrame:
    """
    Proyecta `steps` meses aplicando shocks instantáneos.
    Ejemplo:
        shocks_dict = {"policy_rate": {"magnitude": 3.0},
                       "inflation":   {"magnitude": 0.4},
                       "gdp":         {"magnitude": -1.0}}
    """
    p       = results.k_ar
    history = results.endog[-p:].copy()

    for var, cfg in shocks_dict.items():
        if var not in results.names:
            raise ValueError(f"'{var}' no está en el VAR.")
        idx = results.names.index(var)
        history[-1, idx] += cfg["magnitude"]

    forecast  = results.forecast(history, steps=steps)
    last_date = pd.to_datetime(results.dates[-1])
    idx       = pd.date_range(last_date + pd.offsets.MonthBegin(1),
                              periods=steps, freq="MS")
    return pd.DataFrame(forecast, columns=results.names, index=idx)


# ────────────────────────────────────────────────────────────────
# Simulación de shocks persistentes (nuevo)
# ────────────────────────────────────────────────────────────────
def simulate_var_shock_persistent(
    results,
    shocks_dict: dict,
    steps: int = 12,
    shock_duration: int = 3,
    shock_decay: float = 0.8
) -> pd.DataFrame:
    """
    Simula shocks PERSISTENTES con decaimiento gradual.
    - El shock se aplica durante 'shock_duration' periodos.
    - En cada periodo, el shock decae multiplicando por 'shock_decay'**t.
    - Si shock_duration=1 y shock_decay=1.0, es equivalente a un shock instantáneo.

    Args:
        results: Modelo VAR entrenado
        shocks_dict: {var: {"magnitude": float}}
        steps: meses a simular
        shock_duration: duración del shock (meses)
        shock_decay: factor de decaimiento (0 < decay <= 1)
    Returns:
        DataFrame con la simulación
    """
    p = results.k_ar
    history = results.endog[-p:].copy()
    n_vars = len(results.names)

    # Crear matriz de shocks persistentes
    shock_matrix = np.zeros((steps, n_vars))
    for var, cfg in shocks_dict.items():
        if var not in results.names:
            raise ValueError(f"'{var}' no está en el VAR.")
        idx = results.names.index(var)
        magnitude = cfg["magnitude"]
        for t in range(min(shock_duration, steps)):
            decay_factor = shock_decay ** t
            shock_matrix[t, idx] = magnitude * decay_factor

    # Simular paso a paso con shocks persistentes
    forecasts = []
    current_history = history.copy()
    for t in range(steps):
        # Aplicar shock en este periodo
        current_history[-1] += shock_matrix[t]
        # Forecast de un paso
        forecast_step = results.forecast(current_history, steps=1)
        forecasts.append(forecast_step[0])
        # Actualizar historia
        current_history = np.vstack([current_history[1:], forecast_step])

    # Crear DataFrame con fechas
    last_date = pd.to_datetime(results.dates[-1])
    idx = pd.date_range(last_date + pd.offsets.MonthBegin(1), periods=steps, freq="MS")
    return pd.DataFrame(forecasts, columns=results.names, index=idx)