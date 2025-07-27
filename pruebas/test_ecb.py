from api.ecb import get_series_ecb

# ⚠️ CLAVE CORRECTA para IPC Eurozona, sin ajuste, sin impuestos
df = get_series_ecb("ICP", "M.U2.N.000000.4.INX")
print(df.head())
