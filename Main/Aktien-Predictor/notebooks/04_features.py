import pandas as pd
import duckdb

# Daten aus Datenbank laden
con = duckdb.connect("../warehouse/aktien.db")
df = con.execute("SELECT * FROM aktien").fetchdf()
con.close()

# Index setzen
df.index = pd.to_datetime(df.index)
df = df.sort_index()

# Features erstellen
df["MA7"] = df["Close"].rolling(window=7).mean()    # 7-Tage Durchschnitt
df["MA30"] = df["Close"].rolling(window=30).mean()  # 30-Tage Durchschnitt
df["Lag1"] = df["Close"].shift(1)                   # Kurs von gestern
df["Lag2"] = df["Close"].shift(2)                   # Kurs von vorgestern

# Ziel: Morgiger Kurs
df["Target"] = df["Close"].shift(-1)

# Zeilen mit NaN entfernen
df = df.dropna()

print(df.head(10))
print(f"\nForm: {df.shape}")
print(f"\nSpalten: {df.columns.tolist()}")

# Zurück in Datenbank speichern
con = duckdb.connect("../warehouse/aktien.db")
con.execute("DROP TABLE IF EXISTS aktien_features")
con.execute("CREATE TABLE aktien_features AS SELECT * FROM df")
con.close()

print("\nFeatures gespeichert!")
