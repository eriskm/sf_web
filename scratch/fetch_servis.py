import sqlite3
conn = sqlite3.connect('sukabumi_flasher.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('SELECT "Nama User", Status, "Harga Jual" FROM servis')
data = cur.fetchall()
for row in data:
    print(dict(row))
