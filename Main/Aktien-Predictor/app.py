import streamlit as st
import pandas as pd
import duckdb
import joblib
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Aktien-Predictor", page_icon="📈", layout="wide")

st.title("📈 Aktien-Predictor")
st.markdown("Machine Learning Vorhersage für Aktienkurse")

# Sidebar
st.sidebar.header("Einstellungen")
ticker = st.sidebar.selectbox("Aktie auswählen", ["AAPL", "MSFT", "NVDA", "GOOGL"])

# Daten laden
@st.cache_data
def lade_daten(ticker):
    import os
    db_pfad = os.path.join(os.path.dirname(__file__), "warehouse", "aktien.db")
    con = duckdb.connect(db_pfad)
    df = con.execute(f"SELECT * FROM features WHERE Ticker = '{ticker}' ORDER BY Date").fetchdf()
    con.close()
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = lade_daten(ticker)

# Aktuelle Werte anzeigen
col1, col2, col3, col4 = st.columns(4)
col1.metric("Aktueller Kurs", f"${df['Close'].iloc[-1]:.2f}")
col2.metric("RSI", f"{df['RSI'].iloc[-1]:.1f}")
col3.metric("MA7", f"${df['MA7'].iloc[-1]:.2f}")
col4.metric("BB Breite", f"${df['BB_breite'].iloc[-1]:.2f}")

# Kursverlauf
st.subheader("Kursverlauf")
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(df["Date"], df["Close"], label="Close", color="blue")
ax.plot(df["Date"], df["MA7"], label="MA7", color="orange", linestyle="--")
ax.plot(df["Date"], df["MA30"], label="MA30", color="green", linestyle="--")
ax.legend()
ax.set_xlabel("Datum")
ax.set_ylabel("Preis (USD)")
st.pyplot(fig)

# Vorhersage
st.subheader("Vorhersage für morgen")

try:
    
    modell_pfad = os.path.join(os.path.dirname(__file__), "model", "bestes_modell.pkl")
    modell = joblib.load(modell_pfad)
    features = ["Return", "MA7", "MA30", "Lag1", "Lag2",
                "RSI", "BB_breite", "Volumen_MA"]
    
    df["Return"] = df["Close"].pct_change()
    letzter_tag = df[features].iloc[-1:]
    vorhersage = modell.predict(letzter_tag)[0]
    
    kurs_morgen = df["Close"].iloc[-1] * (1 + vorhersage)
    
    col1, col2 = st.columns(2)
    col1.metric("Vorhergesagter Kurs morgen", f"${kurs_morgen:.2f}")
    col2.metric("Erwartete Veränderung", f"{vorhersage*100:.2f}%",
                delta=f"{vorhersage*100:.2f}%")

except Exception as e:
    st.warning(f"Modell nicht gefunden — führe zuerst 09_modellvergleich.py aus. ({e})")

# RSI Chart
st.subheader("RSI Verlauf")
fig2, ax2 = plt.subplots(figsize=(12, 3))
ax2.plot(df["Date"], df["RSI"], color="purple")
ax2.axhline(y=70, color="red", linestyle="--", label="Überkauft (70)")
ax2.axhline(y=30, color="green", linestyle="--", label="Überverkauft (30)")
ax2.legend()
ax2.set_ylabel("RSI")
st.pyplot(fig2)

st.markdown("---")
st.markdown("Aktien-Predictor | Nico | ZHAW Data Science")
