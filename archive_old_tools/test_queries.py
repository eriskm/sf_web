import sqlite3
from datetime import datetime
conn = sqlite3.connect('sukabumi_flasher.db')
conn.row_factory = sqlite3.Row
tgl_hari_ini = datetime.now().strftime('%Y-%m-%d')
try:
    print('Masuk:', conn.execute('SELECT COUNT(*) FROM servis WHERE "Tanggal Masuk" = ?', (tgl_hari_ini,)).fetchone()[0])
    print('Selesai:', conn.execute('SELECT COUNT(*) FROM servis WHERE updated_at LIKE ? AND Status IN ("Done", "Cash")', (f'{tgl_hari_ini}%',)).fetchone()[0])
    print('Pending:', conn.execute('SELECT COUNT(*) FROM servis WHERE Status IN ("Analisa", "Konfirmasi", "Wait Part", "Repair")').fetchone()[0])
    print('Tech:', conn.execute('SELECT Teknisi, SUM("Harga Jual") as revenue, COUNT(*) as jobs FROM servis WHERE updated_at LIKE ? AND Status = "Cash" AND Teknisi IS NOT NULL AND TRIM(Teknisi) != "" GROUP BY Teknisi ORDER BY revenue DESC LIMIT 1', (f'{tgl_hari_ini}%',)).fetchone())
except Exception as e:
    print('ERROR:', e)
