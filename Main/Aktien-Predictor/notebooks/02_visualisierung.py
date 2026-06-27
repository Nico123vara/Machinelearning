import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt

# Korrekt laden - erste 2 Zeilen überspringen
df = pd.read_csv("../data/AAPL.csv", skiprows=[0, 1], index_col=0, parse_dates=True)
df.columns = ["Close", "High", "Low", "Open", "Volume"]
df = df.dropna()

print(df.head())

plt.figure(figsize=(12, 5))
plt.plot(df.index, df["Close"].astype(float))
plt.title("Apple Aktienkurs 2023-2024")
plt.xlabel("Datum")
plt.ylabel("Preis (USD)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("../data/chart.png")
print("Chart gespeichert!")