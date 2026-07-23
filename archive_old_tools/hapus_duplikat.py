import sqlite3

conn = sqlite3.connect('sukabumi_flasher.db')
cursor = conn.cursor()

# Hapus baris yang namanya sama, sisakan yang ID-nya paling kecil
cursor.execute('''
    DELETE FROM beban 
    WHERE id NOT IN (
        SELECT MIN(id) 
        FROM beban 
        GROUP BY nama_beban
    )
''')

print(f"Data dibersihkan! {cursor.rowcount} baris duplikat dihapus.")
conn.commit()
conn.close()