# pruebas/test_save_series.py

from api.fred import get_series_fred
from api.ecb import get_series_ecb
from utils.io import save_series
from utils.transform import normalize_series

# --- Real GDP USA ---
df_gdp = get_series_fred("GDPC1")
df_gdp = normalize_series(df_gdp, "real_gdp_usa")
save_series(df_gdp, "real_gdp_usa")

# --- HICP Euro Area ---
df_hicp = get_series_ecb("ICP", "M.U2.N.000000.4.INX")
df_hicp = normalize_series(df_hicp, "hicp_ea")
save_series(df_hicp, "hicp_ea")
