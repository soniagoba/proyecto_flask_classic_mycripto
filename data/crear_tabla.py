import sqlite3

con = sqlite3.connect("data/operaciones.db")
cur = con.cursor()

sql = '''CREATE TABLE "operaciones" (
	"id"	INTEGER,
	"date"	TEXT NOT NULL,
	"time"	TEXT NOT NULL,
	"moneda_from"	TEXT NOT NULL,
	"cantidad_from"	REAL NOT NULL,
    "moneda_to"	TEXT NOT NULL,
	"cantidad_to"	REAL NOT NULL,
	"precio_unitario" REAL NOT NULL,
	"tasa" REAL NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)'''

cur.execute(sql)
print("Tabla creada correctamente.")

con.commit()
con.close()