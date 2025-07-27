# pruebas/test_pipeline.py
from etl.pipeline import run_etl_pipeline

VARIABLES = {
    "real_gdp_usa": {
        "source": "FRED",
        "id": "GDPC1"
    },
    "hicp_ea": {
        "source": "ECB",
        "dataset": "ICP",
        "key": "M.U2.N.000000.4.INX"
    }
}

if __name__ == "__main__":
    run_etl_pipeline(VARIABLES)
