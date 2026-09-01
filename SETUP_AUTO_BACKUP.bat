@echo off
setlocal
cd /d "%~dp0"
set "PYTHONW=%~dp0.venv\Scripts\pythonw.exe"
set "BACKUP_SCRIPT=%~dp0auto_backup.py"
if not exist "%PYTHONW%" (
    echo [ERROR] pythonw.exe tidak ditemukan. Jalankan SETUP_PC_BARU.bat.
    pause
    exit /b 1
)
schtasks /create /tn "SF_BOSS_AutoBackup" /tr "\"%PYTHONW%\" \"%BACKUP_SCRIPT%\"" /sc daily /st 07:30 /f
if errorlevel 1 (
    echo [ERROR] Gagal membuat jadwal. Jalankan file ini sebagai Administrator.
    pause
    exit /b 1
)
echo Jadwal backup MySQL harian pukul 07:30 berhasil dibuat.
pause