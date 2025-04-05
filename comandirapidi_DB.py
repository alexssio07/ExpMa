import sqlite3

conn = sqlite3.connect("expma_db.db")
cur = conn.cursor()

cur.execute("DELETE FROM spesa;")
conn.commit()
conn.close()
