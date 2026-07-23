import sqlite3
conn = sqlite3.connect('sukabumi_flasher.db')
cursor = conn.cursor()
cursor.execute("SELECT rowid, `Tanggal Masuk`, Status, `Tindakan Perbaikan` FROM servis LIMIT 5")
for row in cursor.fetchall():
    print(row)
