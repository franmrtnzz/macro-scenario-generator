# api/fred.py

import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

def get_series_fred(series_id: str) -> pd.DataFrame:
    """
    Descarga una serie temporal desde la API de FRED y la devuelve como DataFrame.
    """
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY is required to refresh FRED data.")

    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    observations = data["observations"]
    records = [(obs["date"], obs["value"]) for obs in observations]

    df = pd.DataFrame(records, columns=["date", "value"])
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("date").sort_index()
