import pandas as pd
import duckdb
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Daten laden
con = duckdb.connect("../warehouse/aktien.db")
df = con.execute("SELECT * FROM features WHERE Ticker = 'AAPL' ORDER BY Date").fetchdf()
con.close()

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")

# Prozentuale Veränderung statt absolute Kurse
df["Return"] = df["Close"].pct_change()
df["Target_Return"] = df["Target"] / df["Close"] - 1
df = df.dropna()

# Features — keine absoluten Kurse mehr
features = ["Return", "MA7", "MA30", "Lag1", "Lag2",
            "RSI", "BB_breite", "Volumen_MA"]
X = df[features]
y = df["Target_Return"]

# Train/Test Split
split = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

print(f"Training: {len(X_train)} Tage")
print(f"Test: {len(X_test)} Tage")

# Modelle
modelle = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
}

resultate = {}

for name, modell in modelle.items():
    modell.fit(X_train, y_train)
    y_pred = modell.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    resultate[name] = {"rmse": rmse, "mae": mae, "pred": y_pred}
    print(f"\n{name}:")
    print(f"  RMSE: {rmse:.4f} (% Veränderung)")
    print(f"  MAE:  {mae:.4f} (% Veränderung)")

# Bestes Modell
bestes = min(resultate, key=lambda x: resultate[x]["rmse"])
print(f"\nBestes Modell: {bestes}")
joblib.dump(modelle[bestes], "../model/bestes_modell.pkl")

# Feature Importance
rf = modelle["Random Forest"]
importance = pd.DataFrame({
    "Feature": features,
    "Importance": rf.feature_importances_
}).sort_values("Importance", ascending=False)
print(f"\nFeature Importance:")
print(importance.to_string(index=False))

# Chart
fig, axes = plt.subplots(2, 1, figsize=(12, 10))

axes[0].plot(y_test.values, label="Echter Return", color="blue")
for name, r in resultate.items():
    axes[0].plot(r["pred"], label=name, linestyle="--", alpha=0.7)
axes[0].set_title("Vorhersage vs Realität (% Veränderung)")
axes[0].legend()

axes[1].barh(importance["Feature"], importance["Importance"], color="steelblue")
axes[1].set_title("Feature Importance (Random Forest)")
axes[1].invert_yaxis()

plt.tight_layout()
plt.savefig("../data/modellvergleich.png")
print("\nChart gespeichert!")
