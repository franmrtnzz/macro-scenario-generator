# utils/io.py
import pandas as pd
from pathlib import Path

# Carpeta raíz /data
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def save_series(df: pd.DataFrame, name: str) -> None:
    """
    Guarda un DataFrame en CSV y pickle dentro de /data.

    Parámetros
    ----------
    df   : pd.DataFrame  (columnas: ['date', 'variable', 'value'])
    name : str           (prefijo de archivo, ej. 'real_gdp_usa')

    Crea:
    - data/<name>.csv
    - data/<name>.pkl
    """
    DATA_DIR.mkdir(exist_ok=True)

    csv_path = DATA_DIR / f"{name}.csv"
    pkl_path = DATA_DIR / f"{name}.pkl"

    # Guarda en disco
    df.to_csv(csv_path, index=False)
    df.to_pickle(pkl_path)

    print(f"✅ Guardado {name}:")
    print(f"   - CSV : {csv_path}")
    print(f"   - PKL : {pkl_path}")
