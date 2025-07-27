# quant/input_validation.py

from datetime import datetime

# Variables macroeconómicas válidas en el modelo
VALID_VARIABLES = ["gdp", "inflation", "interest_rate", "equity"]

def validate_shocks(shocks_dict, available_dates):
    for var, config in shocks_dict.items():
        # Validar nombre de la variable
        if var not in VALID_VARIABLES:
            raise ValueError(f"Variable no válida: {var}")

        # Validar tipo de shock
        if config["shock_type"] not in ["increase", "decrease"]:
            raise ValueError(f"Tipo de shock no válido para {var}: {config['shock_type']}")

        # Validar que el valor sea numérico
        if not isinstance(config["value"], (int, float)):
            raise ValueError(f"Valor no numérico para {var}: {config['value']}")

        # Validar formato de fecha
        try:
            datetime.strptime(config["start"], "%Y-%m")
        except ValueError:
            raise ValueError(f"Formato de fecha incorrecto en {var}: {config['start']}")

        # Validar que la fecha esté en las series históricas
        if config["start"] not in available_dates:
            raise ValueError(f"La fecha {config['start']} no existe en las series disponibles")

    print("✅ Validación completada correctamente")
