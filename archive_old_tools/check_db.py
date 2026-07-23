import sqlite3
conn = sqlite3.connect('sukabumi_flasher.db')
conn.row_factory = sqlite3.Row
res = conn.execute('SELECT "Analisa Kerusakan", COUNT(*) as cnt FROM servis GROUP BY "Analisa Kerusakan" ORDER BY cnt DESC LIMIT 20').fetchall()
for r in res:
    print(f"{r[0]}: {r[1]}")
