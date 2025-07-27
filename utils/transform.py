# utils/transform.py
import pandas as pd

def normalize_series(df: pd.DataFrame, var_name: str | None = None) -> pd.DataFrame:
    """
    Normaliza una serie (min-max).  
    Si se pasa `var_name`, añade columna 'variable'.

    Parameters
    ----------
    df : pd.DataFrame
        Índice fecha + columna 'value'.
    var_name : str | None
        Nombre interno de la variable.

    Returns
    -------
    pd.DataFrame
        • Sin var_name  → índice + 'value' normalizada.  
        • Con var_name → columnas ['date', 'variable', 'value'].
    """
    df = df.copy()

    # Asegurar que el índice es datetime y mensual
    df = df.sort_index()
    df.index = pd.to_datetime(df.index)
    df = df.asfreq("MS")

    # Normalizar
    min_val = df["value"].min()
    max_val = df["value"].max()
    df["value"] = (df["value"] - min_val) / (max_val - min_val)

    # Caso sin var_name: serie con índice temporal
    if var_name is None:
        return df.sort_index()

    # Caso con var_name: columna 'date' + 'variable' + 'value'
    df = df.reset_index().rename(columns={"index": "date"})
    df["date"] = pd.to_datetime(df["date"])
    df["variable"] = var_name
    df = df[["date", "variable", "value"]]

    return df.sort_values("date")
