# pruebas/test_fred.py

from api.fred import get_series

df = get_series("GDP")  # Producto Interior Bruto de EE. UU.
print(df.head())
