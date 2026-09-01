@echo off
setlocal
cd /d "%~dp0"
title BOT TELEGRAM - SF WEB
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment belum tersedia. Jalankan SETUP_PC_BARU.bat.
    pause
    exit /b 1
)
echo Menjalankan bot Telegram SF_WEB...
".venv\Scripts\python.exe" services\telegram_bot.py
set "EXIT_CODE=%ERRORLEVEL%"
echo Bot berhenti dengan exit code %EXIT_CODE%.
pause
exit /b %EXIT_CODE%