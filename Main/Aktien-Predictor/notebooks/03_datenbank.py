import duckdb
import pandas as pd

# Daten laden
df = pd.read_csv("../data/AAPL.csv", skiprows=[0, 1], index_col=0, parse_dates=True)
df.columns = ["Close", "High", "Low", "Open", "Volume"]
df = df.dropna()
df.index.name = "Date"

# Verbindung zur Datenbank herstellen
con = duckdb.connect("../warehouse/aktien.db")

# Tabelle erstellen und Daten speichern
con.execute("DROP TABLE IF EXISTS aktien")
con.execute("""
    CREATE TABLE aktien AS
    SELECT * FROM df
""")

# Kontrolle
result = con.execute("SELECT * FROM aktien LIMIT 5").fetchdf()
print(result)
print(f"\nAnzahl Zeilen in DB: {con.execute('SELECT COUNT(*) FROM aktien').fetchone()[0]}")

con.close()
print("\nDatenbank gespeichert!")
