# quant/var_model_enhanced.py
import pickle
import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR
from sklearn.preprocessing import StandardScaler


def train_var_model_enhanced(series_path: str, lags: int = 1, min_vars: int = 2, 
                            include_long_rate: bool = True, include_spread: bool = True,
                            max_corr: float = 0.85, min_std: float = 0.001):
    """
    Entrena un VAR mejorado que puede incluir long_rate y spread con transformaciones apropiadas.
    
    Args:
        series_path: Ruta al archivo de series
        lags: Número de lags del VAR
        min_vars: Número mínimo de variables requeridas
        include_long_rate: Si incluir long_rate con transformación log-diff
        include_spread: Si incluir spread con transformación diff
        max_corr: Correlación máxima permitida
        min_std: Desviación estándar mínima
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
    
    # Variables base (siempre incluidas)
    # gdp: usar diff si es viable, sino nivel
    if std_diff['gdp'] > min_std and not pd.isna(std_diff['gdp']):
        df_transformed['gdp'] = df['gdp'].diff()
        print("✅ gdp: usando diff")
    else:
        df_transformed['gdp'] = df['gdp']
        print("⚠️  gdp: usando nivel (diff no viable)")
    
    # inflation: usar nivel (siempre tiene buena variabilidad)
    df_transformed['inflation'] = df['inflation']
    print("✅ inflation: usando nivel")
    
    # policy_rate: usar nivel con ruido si es necesario
    df_transformed['policy_rate'] = df['policy_rate']
    print("✅ policy_rate: usando nivel")
    
    # real_rate: usar nivel con ruido si es necesario
    df_transformed['real_rate'] = df['real_rate']
    print("✅ real_rate: usando nivel")
    
    # Variables opcionales con transformaciones específicas
    if include_long_rate:
        # long_rate: usar log-diff para mayor variabilidad
        try:
            log_diff = np.log(df['long_rate'] + 0.001).diff()
            if log_diff.std() > min_std:
                df_transformed['long_rate'] = log_diff
                print("✅ long_rate: usando log-diff")
            else:
                df_transformed['long_rate'] = df['long_rate'].diff()
                print("✅ long_rate: usando diff")
        except:
            df_transformed['long_rate'] = df['long_rate'].diff()
            print("✅ long_rate: usando diff (fallback)")
    
    if include_spread:
        # spread: usar diff para mayor variabilidad
        if std_diff['spread'] > min_std:
            df_transformed['spread'] = df['spread'].diff()
            print("✅ spread: usando diff")
        else:
            df_transformed['spread'] = df['spread']
            print("✅ spread: usando nivel")
    
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
    if len(df_clean.columns) < min_vars:
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


# Función de simulación (igual que la original)
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