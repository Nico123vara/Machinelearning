import pandas as pd
import duckdb
import numpy as np

def berechne_rsi(series, periode=14):
    delta = series.diff()
    gewinn = delta.where(delta > 0, 0)
    verlust = -delta.where(delta < 0, 0)
    avg_gewinn = gewinn.rolling(window=periode).mean()
    avg_verlust = verlust.rolling(window=periode).mean()
    rs = avg_gewinn / avg_verlust
    rsi = 100 - (100 / (1 + rs))
    return rsi

def berechne_bollinger(series, periode=20):
    ma = series.rolling(window=periode).mean()
    std = series.rolling(window=periode).std()
    obere_band = ma + (2 * std)
    untere_band = ma - (2 * std)
    return ma, obere_band, untere_band

# Daten laden
con = duckdb.connect("../warehouse/aktien.db")
df = con.execute("SELECT * FROM alle_aktien ORDER BY Ticker, Date").fetchdf()
con.close()

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values(["Ticker", "Date"])

# Features pro Ticker berechnen
alle_ticker = []

for ticker in df["Ticker"].unique():
    t = df[df["Ticker"] == ticker].copy()

    # Bestehende Features
    t["MA7"] = t["Close"].rolling(7).mean()
    t["MA30"] = t["Close"].rolling(30).mean()
    t["Lag1"] = t["Close"].shift(1)
    t["Lag2"] = t["Close"].shift(2)

    # Neue Features
    t["RSI"] = berechne_rsi(t["Close"])
    t["MA20"], t["BB_oben"], t["BB_unten"] = berechne_bollinger(t["Close"])
    t["BB_breite"] = t["BB_oben"] - t["BB_unten"]
    t["Volumen_MA"] = t["Volume"].rolling(10).mean()

    # Ziel
    t["Target"] = t["Close"].shift(-1)

    alle_ticker.append(t)

# Zusammenfügen
gesamt = pd.concat(alle_ticker).dropna()
print(f"Form: {gesamt.shape}")
print(f"Spalten: {gesamt.columns.tolist()}")

# In DB speichern
con = duckdb.connect("../warehouse/aktien.db")
con.execute("DROP TABLE IF EXISTS features")
con.execute("CREATE TABLE features AS SELECT * FROM gesamt")
con.close()

print("\nFeatures gespeichert!")
