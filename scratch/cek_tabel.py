import sqlite3
conn = sqlite3.connect('sukabumi_flasher.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(table[0])
    # Print columns for each table to find the sparepart one
    cursor.execute(f"PRAGMA table_info({table[0]})")
    cols = cursor.fetchall()
    print([c[1] for c in cols])
conn.close()
