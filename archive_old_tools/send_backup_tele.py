import os
import shutil
import requests
from datetime import datetime

# Konfigurasi Bot Telegram (Menggunakan bot yang sudah ada di app.py)
TOKEN = '8670230633:AAF91XoMmWQtEM2yN3nF-sLwpTJPJ-XqEiY'
CHAT_ID = '-429882392'

# Konfigurasi Path File
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'sukabumi_flasher.db')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

now_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
backup_filename = f'backup_db_auto_{now_str}.db'
backup_filepath = os.path.join(BACKUP_DIR, backup_filename)

try:
    # 1. Copy database ke folder backups lokal
    shutil.copy2(DB_PATH, backup_filepath)
    print(f"Database berhasil dibackup secara lokal: {backup_filename}")
    
    # 2. Kirim file .db ke Telegram
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    pesan = f"🔒 *AUTO BACKUP DATABASE HARIAN*\n📅 Tanggal: {datetime.now().strftime('%d %B %Y %H:%M')}\n\nIni adalah backup rutin otomatis database BOSS jam 07:30 pagi. File ini bisa digunakan untuk me-*restore* data jika PC mengalami masalah."
    
    with open(backup_filepath, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': CHAT_ID, 'caption': pesan, 'parse_mode': 'Markdown'}
        response = requests.post(url, files=files, data=data)
        
    if response.status_code == 200:
        print("Backup berhasil dikirim ke Telegram dengan aman!")
    else:
        print(f"Gagal mengirim ke Telegram. Status: {response.status_code}, Respon: {response.text}")

    # Opsional: Bersihkan file backup lama agar harddisk tidak kepenuhan (sisakan 15 hari terakhir)
    all_backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith('backup_db_auto_') and f.endswith('.db')]
    all_backups.sort()
    if len(all_backups) > 15:
        for old_file in all_backups[:-15]:
            try:
                os.remove(os.path.join(BACKUP_DIR, old_file))
            except Exception:
                pass

except Exception as e:
    print(f"Terjadi kesalahan saat proses backup: {e}")
