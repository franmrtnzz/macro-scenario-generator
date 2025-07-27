# quant/shock_propagation.py
import pandas as pd

def apply_shocks(series_dict, shocks, rules):
    """
    Aplica los shocks definidos por el usuario sobre las series históricas
    utilizando reglas causales simples (multiplicadores fijos).

    Parameters
    ----------
    series_dict : dict[str, pd.Series]
        Series históricas originales (gdp, inflation, etc.)
    shocks : dict
        Diccionario de shocks del usuario
    rules : dict
        Multiplicadores que enlazan la variable shock con la variable afectada

    Returns
    -------
    dict[str, pd.Series]
        Nuevo diccionario con las series ajustadas
    """
    # Copiamos las series para no modificar las originales
    new_series = {k: v.copy() for k, v in series_dict.items()}

    # Recorremos cada shock definido por el usuario
    for shocked_var, config in shocks.items():
        # Valor del shock positivo o negativo
        shock_value = config["value"] if config["shock_type"] == "increase" else -config["value"]
        start_date = config["start"]

        # Reglas que indican qué variables se ven afectadas y con qué multiplicador
        for affected_var, multiplier in rules.get(shocked_var, {}).items():
            if affected_var in new_series:
                # ⚠️ Solo aplicamos si la serie es numérica (evitamos fechas u objetos)
                if not pd.api.types.is_numeric_dtype(new_series[affected_var]):
                    print(
                        f"⛔️  La serie '{affected_var}' no es numérica; "
                        "se omite el shock sobre ella."
                    )
                    continue

                # Aplicar el efecto multiplicador desde la fecha indicada
                new_series[affected_var].loc[start_date:] += shock_value * multiplier

    return new_series
