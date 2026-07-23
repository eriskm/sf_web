@echo off
schtasks /create /tn "SF_BOSS_AutoBackup" /tr "\"E:\SFS PROJECK\SF_WEB\.venv\Scripts\pythonw.exe\" \"E:\SFS PROJECK\SF_WEB\auto_backup.py\"" /sc daily /st 07:30 /f
