import pandas as pd
import duckdb
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np

# Daten aus Datenbank laden
con = duckdb.connect("../warehouse/aktien.db")
df = con.execute("SELECT * FROM aktien_features").fetchdf()
con.close()

df.index = pd.to_datetime(df.index)
df = df.sort_index()

# Features und Ziel definieren
features = ["Close", "High", "Low", "Open", "Volume", "MA7", "MA30", "Lag1", "Lag2"]
X = df[features]
y = df["Target"]

# Train/Test Split - WICHTIG: chronologisch, nicht zufällig!
split = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

print(f"Training: {len(X_train)} Tage")
print(f"Test: {len(X_test)} Tage")

# Modell 1: Lineare Regression
lr = LinearRegression()
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)

# Modell 2: Random Forest
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)

# Resultate
rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
mae_lr = mean_absolute_error(y_test, y_pred_lr)
mae_rf = mean_absolute_error(y_test, y_pred_rf)

print(f"\nLineare Regression:")
print(f"  RMSE: {rmse_lr:.2f} USD")
print(f"  MAE:  {mae_lr:.2f} USD")

print(f"\nRandom Forest:")
print(f"  RMSE: {rmse_rf:.2f} USD")
print(f"  MAE:  {mae_rf:.2f} USD")
