import sqlite3
conn = sqlite3.connect('sukabumi_flasher.db')

# 1. Hapus data yang double dulu biar bersih
conn.execute('DELETE FROM beban WHERE rowid NOT IN (SELECT MIN(rowid) FROM beban GROUP BY nama_beban, nilai)')

# 2. Tambahkan pengaman UNIQUE biar nggak bisa double lagi kedepannya
# Karena SQLite tidak bisa langsung ALTER UNIQUE, kita buat tabel baru yang aman
conn.execute('CREATE TABLE beban_baru (id INTEGER PRIMARY KEY AUTOINCREMENT, kategori TEXT, nama_beban TEXT UNIQUE, nilai INTEGER)')
conn.execute('INSERT INTO beban_baru SELECT * FROM beban')
conn.execute('DROP TABLE beban')
conn.execute('ALTER TABLE beban_baru RENAME TO beban')

conn.commit()
conn.close()
print("Database AIS Technologies sudah dipasang pengaman UNIQUE!")