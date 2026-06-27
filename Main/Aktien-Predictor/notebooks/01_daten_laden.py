import yfinance as yf
import pandas as pd

df = yf.download("AAPL", start="2023-01-01", end="2024-12-31")

print(df.head())
print(df.shape)
print(df.columns.tolist())

df.to_csv("../data/AAPL.csv")
print("Gespeichert!")