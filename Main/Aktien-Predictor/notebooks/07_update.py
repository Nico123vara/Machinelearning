import yfinance as yf
import pandas as pd
import duckdb
from datetime import datetime, timedelta

# Aktien Liste
aktien = ["AAPL", "MSFT", "NVDA", "GOOGL"]

# Verbindung zur Datenbank
con = duckdb.connect("../warehouse/aktien.db")

# Letztes Datum in der DB prüfen
letztes_datum = con.execute("SELECT MAX(Date) FROM alle_aktien").fetchone()[0]
print(f"Letztes Datum in DB: {letztes_datum}")

# Ab morgen nach dem letzten Datum laden
start = (pd.to_datetime(letztes_datum) + timedelta(days=1)).strftime("%Y-%m-%d")
ende = datetime.today().strftime("%Y-%m-%d")

print(f"Lade neue Daten von {start} bis {ende}...")

if start >= ende:
    print("Keine neuen Daten — DB ist bereits aktuell!")
else:
    neue_daten = []

    for ticker in aktien:
        df = yf.download(ticker, start=start, end=ende, auto_adjust=True)
        if len(df) == 0:
            print(f"{ticker}: keine neuen Daten")
            continue
        df.columns = ["Close", "High", "Low", "Open", "Volume"]
        df = df.dropna()
        df.index.name = "Date"
        df = df.reset_index()
        df["Ticker"] = ticker
        neue_daten.append(df)
        print(f"{ticker}: {len(df)} neue Zeilen")

    if neue_daten:
        gesamt = pd.concat(neue_daten)
        con.execute("INSERT INTO alle_aktien SELECT * FROM gesamt")
        print(f"\n{len(gesamt)} neue Zeilen hinzugefügt!")

total = con.execute("SELECT COUNT(*) FROM alle_aktien").fetchone()[0]
print(f"Total in DB: {total} Zeilen")
con.close()
