import sqlite3
conn = sqlite3.connect('sukabumi_flasher.db')
try:
    conn.execute('ALTER TABLE servis ADD COLUMN PassWord TEXT')
    print("Kolom PassWord berhasil ditambah!")
except:
    print("Kolom mungkin sudah ada.")
conn.close()