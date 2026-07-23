import os
import shutil
from datetime import datetime

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

    # 2. Bersihkan file backup lama agar harddisk (dan Google Drive) tidak kepenuhan (sisakan 15 hari terakhir)
    all_backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith('backup_db_auto_') and f.endswith('.db')]
    all_backups.sort()
    if len(all_backups) > 15:
        for old_file in all_backups[:-15]:
            try:
                os.remove(os.path.join(BACKUP_DIR, old_file))
                print(f"File lama dihapus: {old_file}")
            except Exception:
                pass

    print("Proses backup lokal selesai! Google Drive akan otomatis meng-upload file ini ke cloud.")

except Exception as e:
    print(f"Terjadi kesalahan saat proses backup: {e}")
