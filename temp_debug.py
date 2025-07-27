import pickle, pandas as pd

with open("data/series.pkl", "rb") as f:
    raw = pickle.load(f)

df = pd.DataFrame({k: pd.Series(v) for k, v in raw.items()})
df = df.sort_index().ffill().loc["1970-01-01":]

df_diff = df.diff()
df_pct = df.pct_change(fill_method=None)

df_mix = pd.concat([
    df_diff[["gdp"]],
    df_pct[["inflation", "policy_rate", "long_rate", "spread", "real_rate"]]
], axis=1)

df_mix = df_mix[df_mix.notna().sum(axis=1) >= 3]

stds = df_mix.std()

print("\n▶️ DESVIACIÓN TÍPICA POR VARIABLE:")
print(stds)
