import zipfile
import os
from datetime import datetime

backup_name = f"SF_WEB_BACKUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
print(f"Creating backup: {backup_name}")

with zipfile.ZipFile(backup_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', '.git', '.agent', 'backups', 'gemma-gem', 'workspace', 'logs', 'scratch']]
        for file in files:
            if file.endswith('.zip'): continue
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, '.')
            zipf.write(file_path, arcname)

print(f"Backup {backup_name} created successfully.")
