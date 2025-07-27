# pruebas/test_normalize_fred.py

from api.fred import get_series_fred
from utils.transform import normalize_series

# PIB real de EE.UU.
df_raw = get_series_fred("GDPC1")
df_norm = normalize_series(df_raw, "real_gdp_usa")

print(df_norm.head())
