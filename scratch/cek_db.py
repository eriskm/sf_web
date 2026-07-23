import sqlite3
from datetime import datetime

conn = sqlite3.connect('sukabumi_flasher.db')
conn.row_factory = sqlite3.Row

print("--- CEK DATA HARI INI ---")
tgl_skrg = datetime.now().strftime("%Y-%m-%d")
print(f"Mencari Tanggal: {tgl_skrg}")

res_today = conn.execute('SELECT Status, COUNT(*) as jml FROM servis WHERE "Tanggal Masuk" = ? GROUP BY Status', (tgl_skrg,)).fetchall()
for r in res_today:
    print(f"STATUS: {r['Status']} | JUMLAH: {r['jml']}")

print("\n--- 5 TANGGAL TERAKHIR DI DB ---")
res_dates = conn.execute('SELECT "Tanggal Masuk", COUNT(*) as jml FROM servis GROUP BY "Tanggal Masuk" ORDER BY "Tanggal Masuk" DESC LIMIT 5').fetchall()
for r in res_dates:
    print(f"TANGGAL: {r['Tanggal Masuk']} | TOTAL UNIT: {r['jml']}")

conn.close()
