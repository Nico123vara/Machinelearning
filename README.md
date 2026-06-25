# 📈 Aktien-Predictor

Ein persönliches Data Science Projekt zur Vorhersage von Aktienkursen mithilfe von Machine Learning.

---

## 🎯 Ziel

Ich möchte lernen, wie man echte Finanzdaten verarbeitet, speichert und mit einem Machine Learning Modell den Aktienkurs des nächsten Tages vorhersagt. Das Resultat wird auf einer interaktiven Website visualisiert.

---

## 🗂️ Projektphasen

### 1. Daten holen
- Aktienkurse werden über die **Yahoo Finance API** (`yfinance`) automatisch geladen
- Daten: Tägliche Kurse (Open, High, Low, Close, Volume)

### 2. Data Warehouse
- Die Rohdaten werden in einer **DuckDB Datenbank** gespeichert
- Strukturiert und abfragebereit für die Analyse

### 3. Explorative Analyse
- Daten verstehen mit **Pandas** und **Matplotlib**
- Trends, Muster und Ausreisser erkennen

### 4. Machine Learning
- Modell: **Lineare Regression / Random Forest** (scikit-learn)
- Ziel: Aktienkurs von morgen vorhersagen basierend auf historischen Daten

### 5. Website (Bonus)
- Interaktive Visualisierung mit **Streamlit**
- Vorhersage vs. tatsächlicher Kurs als Chart

---

## 🛠️ Technologien

|
 Bereich 
|
 Tool 
|
|
---
|
---
|
|
 Programmiersprache 
|
 Python 
|
|
 Daten holen 
|
 yfinance 
|
|
 Datenverarbeitung 
|
 Pandas 
|
|
 Datenbank 
|
 DuckDB 
|
|
 Machine Learning 
|
 scikit-learn 
|
|
 Visualisierung 
|
 Matplotlib 
|
|
 Website 
|
 Streamlit 
|
|
 Versionskontrolle 
|
 Git / GitHub 
|

---

## 📅 Zeitplan

|
 Wochen 
|
 Phase 
|
|
---
|
---
|
|
 1–2 
|
 Daten holen & verstehen 
|
|
 3–4 
|
 Data Warehouse aufbauen 
|
|
 5–7 
|
 Explorative Analyse 
|
|
 8–10 
|
 ML Modell entwickeln 
|
|
 11–12 
|
 Website & Feinschliff 
|

---

## 📁 Projektstruktur

```
Aktien-Predictor/
│
├── data/           # Rohe Aktiendaten
├── warehouse/      # DuckDB Datenbank
├── notebooks/      # Jupyter Notebooks für Analyse
├── model/          # Trainiertes ML Modell
├── app.py          # Streamlit Website
└── README.md       # Projektbeschreibung
```

---

## 👤 Autor

Nico – Data Science Student @ ZHAW  
Persönliches Ferienprojekt 2025
