import sqlite3
conn = sqlite3.connect('sukabumi_flasher.db')
# Tabel untuk menyimpan kategori beban dan nilainya
conn.execute('''
    CREATE TABLE IF NOT EXISTS beban (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kategori TEXT, -- 'Gaji' atau 'Operasional'
        nama_beban TEXT,
        nilai INTEGER
    )
''')
# Isi data awal biar nggak kosong
conn.execute("INSERT INTO beban (kategori, nama_beban, nilai) VALUES ('Gaji', 'Analize Service Officer', 200000)")
conn.execute("INSERT INTO beban (kategori, nama_beban, nilai) VALUES ('Gaji', 'Customer Service', 200000)")
conn.execute("INSERT INTO beban (kategori, nama_beban, nilai) VALUES ('Operasional', 'Sewa Tempat', 170000)")
conn.commit()
conn.close()
print("Tabel Beban Siap!")