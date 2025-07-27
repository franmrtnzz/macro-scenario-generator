import pickle
import matplotlib.pyplot as plt
import pandas as pd

# Cargar los resultados simulados
with open('data/scenarios/var_run.pkl', 'rb') as f:
    sim = pickle.load(f)

# Representar y guardar el gráfico
sim.plot(figsize=(12, 5), title='VAR – Escenario var_run')
plt.grid(True)
plt.tight_layout()

# Guardar imagen en carpeta figs
plt.savefig('figs/var_run.png', dpi=300, bbox_inches='tight')
plt.close()
