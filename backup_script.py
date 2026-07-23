import os
import zipfile
import datetime

source_dir = 'e:/SFS PROJECK/SF_WEB'
backup_name = f'e:/SFS PROJECK/SF_WEB_BACKUP_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'

def make_backup():
    print("Mulai membuat backup...")
    with zipfile.ZipFile(backup_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            if '.venv' in root or '__pycache__' in root or '.agent' in root:
                continue
            for file in files:
                if file.endswith('.zip'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=os.path.dirname(source_dir))
                zipf.write(file_path, arcname)
    print(f'Backup berhasil dibuat di: {backup_name}')

make_backup()
