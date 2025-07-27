from api.ecb import get_series_ecb
from utils.transform import normalize_series

# IPC armonizado Eurozona
df_raw = get_series_ecb("ICP", "M.U2.N.000000.4.INX")
df_norm = normalize_series(df_raw, "hicp_ea")
print(df_norm.head())
