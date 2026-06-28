import yfinance as yf
import pandas as pd
import duckdb

# Aktien Liste
aktien = ["AAPL", "MSFT", "NVDA", "GOOGL"]

alle_daten = []

for ticker in aktien:
    print(f"Lade {ticker}...")
    df = yf.download(ticker, start="2023-01-01", end="2024-12-31", auto_adjust=True)
    df.columns = ["Close", "High", "Low", "Open", "Volume"]
    df = df.dropna()
    df.index.name = "Date"
    df = df.reset_index()
    df["Ticker"] = ticker  # Ticker-Spalte hinzufügen
    alle_daten.append(df)

# Alle zusammenfügen
gesamt = pd.concat(alle_daten)
print(f"\nTotal Zeilen: {len(gesamt)}")
print(gesamt.head())
print(gesamt.columns)

# In DuckDB speichern
con = duckdb.connect("../warehouse/aktien.db")
con.execute("DROP TABLE IF EXISTS alle_aktien")
con.execute("CREATE TABLE alle_aktien AS SELECT * FROM gesamt")
print(f"\nGespeichert: {con.execute('SELECT COUNT(*) FROM alle_aktien').fetchone()[0]} Zeilen")
con.close()

print("\nFertig!")
