import sqlite3
conn = sqlite3.connect('sukabumi_flasher.db')
conn.row_factory = sqlite3.Row
res = conn.execute('SELECT "Nama User", "No. WA", "Device" FROM servis WHERE "Nama User" LIKE "%erik%"').fetchall()
for r in res:
    print(dict(r))
conn.close()
