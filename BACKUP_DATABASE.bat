@echo off
setlocal
cd /d "%~dp0"
title [SF_WEB] BACKUP DATABASE MYSQL
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment belum tersedia. Jalankan SETUP_PC_BARU.bat.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" export_db.py
set "EXIT_CODE=%ERRORLEVEL%"
pause
exit /b %EXIT_CODE%