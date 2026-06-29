import sys
import os
sys.path.append(os.path.dirname(__file__))
 
from pipeline import AktienPipeline
 
DB_PFAD = "../warehouse/aktien.db"
AKTIEN = ["AAPL", "MSFT", "NVDA", "GOOGL"]
 
for ticker in AKTIEN:
    p = AktienPipeline(ticker, DB_PFAD)
    p.aktie_aktualisieren()
 
print("\nAlle Aktien aktualisiert!")