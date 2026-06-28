import duckdb
con = duckdb.connect("../warehouse/aktien.db")
print(con.execute("DESCRIBE alle_aktien").fetchdf())
con.close()