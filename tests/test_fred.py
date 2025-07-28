import pytest
from api.fred import get_series_fred
import pandas as pd

def test_get_series_fred_gdp():
    """Testea la descarga de la serie GDP desde FRED."""
    df = get_series_fred("GDP")
    # Debe devolver un DataFrame no vacío
    assert isinstance(df, pd.DataFrame)
    assert not df.empty, "El DataFrame está vacío"
    # Debe tener columnas correctas
    assert "value" in df.columns, "Falta columna 'value'"
    # Debe tener fechas como índice
    assert pd.api.types.is_datetime64_any_dtype(df.index), "El índice no es de fechas"
    # Los valores deben ser numéricos y no todos NaN
    assert pd.api.types.is_numeric_dtype(df["value"]), "'value' no es numérico"
    assert df["value"].notna().sum() > 0, "Todos los valores son NaN"
    print(df.head())
