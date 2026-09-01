@echo off
setlocal
cd /d "%~dp0"
title SF WEB APP - V2 (MySQL Native)
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment belum tersedia. Jalankan SETUP_PC_BARU.bat.
    pause
    exit /b 1
)
echo Menjalankan server SF WEB V2...
".venv\Scripts\python.exe" app_v2.py
set "EXIT_CODE=%ERRORLEVEL%"
echo Server berhenti dengan exit code %EXIT_CODE%.
pause
exit /b %EXIT_CODE%