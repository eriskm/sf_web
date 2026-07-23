import sqlite3

# Hubungkan ke database lo
conn = sqlite3.connect('sukabumi_flasher.db')
cursor = conn.cursor()

try:
    # Perintah sakti buat nambah kolom Tindakan Perbaikan
    cursor.execute('ALTER TABLE servis ADD COLUMN "Tindakan Perbaikan" TEXT')
    print("Sip! Kolom 'Tindakan Perbaikan' berhasil ditambah.")
except Exception as e:
    print(f"Pesan: {e}")

conn.commit()
conn.close()