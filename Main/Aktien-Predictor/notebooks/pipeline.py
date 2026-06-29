import pandas as pd
import duckdb
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta


class AktienPipeline:
    def __init__(self, ticker: str, db_pfad: str):
        self.ticker = ticker
        self.db_pfad = db_pfad
        self.df = None

    def _berechne_features_intern(self, df: pd.DataFrame) -> pd.DataFrame:
        """Berechnet alle Features auf einem DataFrame."""
        df = df.copy()

        df["MA7"] = df["Close"].rolling(7).mean()
        df["MA30"] = df["Close"].rolling(30).mean()
        df["Lag1"] = df["Close"].shift(1)
        df["Lag2"] = df["Close"].shift(2)

        # RSI
        delta = df["Close"].diff()
        gewinn = delta.where(delta > 0, 0)
        verlust = -delta.where(delta < 0, 0)
        df["RSI"] = 100 - (100 / (1 + gewinn.rolling(14).mean() / verlust.rolling(14).mean()))

        # Bollinger Bands
        ma20 = df["Close"].rolling(20).mean()
        std20 = df["Close"].rolling(20).std()
        df["MA20"] = ma20
        df["BB_oben"] = ma20 + (2 * std20)
        df["BB_unten"] = ma20 - (2 * std20)
        df["BB_breite"] = df["BB_oben"] - df["BB_unten"]

        df["Volumen_MA"] = df["Volume"].rolling(10).mean()
        df["Target"] = df["Close"].shift(-1)

        return df.dropna()

    def laden(self):
        """Lädt bestehende Daten aus der DB."""
        con = duckdb.connect(self.db_pfad)
        self.df = con.execute(
            f"SELECT * FROM alle_aktien WHERE Ticker = '{self.ticker}' ORDER BY Date"
        ).fetchdf()
        con.close()
        self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.df = self.df.sort_values("Date").reset_index(drop=True)
        print(f"{self.ticker}: {len(self.df)} Zeilen geladen")

    def berechne_features(self):
        """Berechnet alle Features."""
        self.df = self._berechne_features_intern(self.df)
        print(f"{self.ticker}: Features berechnet → {self.df.shape}")

    def speichern(self, tabelle: str = "features"):
        """Speichert Features in DB."""
        con = duckdb.connect(self.db_pfad)
        df = self.df
        con.execute(f"INSERT INTO {tabelle} SELECT * FROM df")
        con.close()
        print(f"{self.ticker}: In '{tabelle}' gespeichert")

    def aktie_hinzufuegen(self, start: str = "2023-01-01"):
        """Fügt eine komplett neue Aktie hinzu."""
        print(f"\nFüge {self.ticker} hinzu...")
        ende = datetime.today().strftime("%Y-%m-%d")

        df = yf.download(self.ticker, start=start, end=ende, auto_adjust=True)
        if len(df) == 0:
            print(f"{self.ticker}: Keine Daten gefunden!")
            return

        df.columns = ["Close", "High", "Low", "Open", "Volume"]
        df = df.dropna()
        df.index.name = "Date"
        df = df.reset_index()
        df["Ticker"] = self.ticker

        con = duckdb.connect(self.db_pfad)
        con.execute("INSERT INTO alle_aktien SELECT * FROM df")
        con.close()

        print(f"{self.ticker}: {len(df)} Zeilen in DB gespeichert")

        self.df = df
        self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.berechne_features()
        self.speichern()

    def aktie_aktualisieren(self):
        """Holt nur neue Tage seit letztem DB-Eintrag."""
        print(f"\nAktualisiere {self.ticker}...")

        con = duckdb.connect(self.db_pfad)
        letztes_datum = con.execute(
            f"SELECT MAX(Date) FROM alle_aktien WHERE Ticker = '{self.ticker}'"
        ).fetchone()[0]
        con.close()

        if letztes_datum is None:
            print(f"{self.ticker}: Noch nicht in DB — benutze aktie_hinzufuegen()")
            return

        start = (pd.to_datetime(letztes_datum) + timedelta(days=1)).strftime("%Y-%m-%d")
        ende = datetime.today().strftime("%Y-%m-%d")

        if start >= ende:
            print(f"{self.ticker}: Bereits aktuell!")
            return

        df_neu = yf.download(self.ticker, start=start, end=ende, auto_adjust=True)
        if len(df_neu) == 0:
            print(f"{self.ticker}: Keine neuen Daten")
            return

        df_neu.columns = ["Close", "High", "Low", "Open", "Volume"]
        df_neu = df_neu.dropna()
        df_neu.index.name = "Date"
        df_neu = df_neu.reset_index()
        df_neu["Ticker"] = self.ticker

        con = duckdb.connect(self.db_pfad)
        con.execute("INSERT INTO alle_aktien SELECT * FROM df_neu")
        con.close()

        print(f"{self.ticker}: {len(df_neu)} neue Zeilen hinzugefügt")

        self.laden()
        self.berechne_features()

        con = duckdb.connect(self.db_pfad)
        con.execute(f"DELETE FROM features WHERE Ticker = '{self.ticker}'")
        df = self.df
        con.execute("INSERT INTO features SELECT * FROM df")
        con.close()
        print(f"{self.ticker}: Features aktualisiert")

    def zusammenfassung(self):
        print(f"\n--- {self.ticker} ---")
        print(f"Zeilen: {len(self.df)}")
        print(f"RSI aktuell: {self.df['RSI'].iloc[-1]:.1f}")
        print(f"Close aktuell: {self.df['Close'].iloc[-1]:.2f} USD")
        print(f"BB_breite aktuell: {self.df['BB_breite'].iloc[-1]:.2f}")


# ── Hauptprogramm ──────────────────────────────────────────────
DB_PFAD = "../warehouse/aktien.db"
AKTIEN = ["AAPL", "MSFT", "NVDA", "GOOGL"]

# Features Tabelle neu erstellen
con = duckdb.connect(DB_PFAD)
con.execute("DROP TABLE IF EXISTS features")
con.execute("""
    CREATE TABLE features (
        Date TIMESTAMP, Close DOUBLE, High DOUBLE, Low DOUBLE,
        Open DOUBLE, Volume BIGINT, Ticker VARCHAR,
        MA7 DOUBLE, MA30 DOUBLE, Lag1 DOUBLE, Lag2 DOUBLE,
        RSI DOUBLE, MA20 DOUBLE, BB_oben DOUBLE, BB_unten DOUBLE,
        BB_breite DOUBLE, Volumen_MA DOUBLE, Target DOUBLE
    )
""")
con.close()

# Pipeline für jede Aktie
pipelines = {}

for ticker in AKTIEN:
    p = AktienPipeline(ticker, DB_PFAD)
    p.laden()
    p.berechne_features()
    p.speichern()
    p.zusammenfassung()
    pipelines[ticker] = p

print(f"\nFertig! {len(pipelines)} Aktien verarbeitet.")
print("\nBeispiele:")
print("  pipelines['AAPL'].aktie_aktualisieren()  # neue Tage holen")
print("  p = AktienPipeline('TSLA', DB_PFAD)")
print("  p.aktie_hinzufuegen()                    # neue Aktie hinzufügen")
