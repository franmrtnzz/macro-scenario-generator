# api/ecb.py
import pandas as pd
import requests

def get_series_ecb(dataset: str, key: str) -> pd.DataFrame:
    """
    Descarga una serie SDMX-JSON desde el nuevo portal ECB
    y la devuelve como DataFrame índice-fecha / columna ‘value’.
    """
    url = f"https://data-api.ecb.europa.eu/service/data/{dataset}/{key}"
    headers = {"Accept": "application/vnd.sdmx.data+json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    # ---- jerarquía actual del endpoint moderno ----
    series_data  = data["dataSets"][0]["series"]
    series_key   = next(iter(series_data))               # única clave de serie
    observations = series_data[series_key]["observations"]

    time_periods = data["structure"]["dimensions"]["observation"][0]["values"]

    records = [
        (time_periods[int(idx)]["name"], obs[0])
        for idx, obs in observations.items()
    ]

    df = pd.DataFrame(records, columns=["date", "value"])
    df["date"]   = pd.to_datetime(df["date"])
    df["value"]  = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("date").sort_index()
