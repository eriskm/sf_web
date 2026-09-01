@echo off
setlocal
cd /d "%~dp0"
title SETUP SF_WEB DI PC BARU
echo ========================================================
echo   SETUP APLIKASI SF_WEB V2
echo ========================================================
if exist ".venv" (
    echo Menghapus virtual environment lama di folder proyek...
    rmdir /s /q ".venv"
)
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Python tidak terdeteksi atau pembuatan venv gagal.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :failed
echo Setup selesai. Isi .env lalu jalankan jalankan_web_v2.bat.
pause
exit /b 0
:failed
echo [ERROR] Instalasi dependency gagal.
pause
exit /b 1