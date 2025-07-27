import pickle
import pandas as pd
import matplotlib.pyplot as plt

with open("data/series.pkl", "rb") as f:
    original = pickle.load(f)

with open("data/scenarios/test_run.pkl", "rb") as f:
    simulated = pickle.load(f)

plt.figure(figsize=(10, 5))
plt.plot(original["inflation"], label="Original", linestyle="--")
plt.plot(simulated["inflation"], label="Simulada", linewidth=2)
plt.axvline(pd.to_datetime("2024-03-01"), color="red", linestyle=":", label="Start shock")
plt.title("Comparativa inflación original vs simulada")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
