@echo off
title Buka Akses Jaringan PC Client - Sukabumi Flasher
net session >nul 2>&1
if %errorLevel% == 0 (
    cls
    echo ================================================================
    echo   MEMBUKA AKSES WINDOWS FIREWALL UNTUK PC CLIENT / HP
    echo ================================================================
    echo.
    echo [1/2] Menambahkan aturan Firewall untuk Port 5000...
    netsh advfirewall firewall add rule name="Sukabumi Flasher Web Port 5000" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1
    echo       Done! Aturan Firewall berhasil dipasang.
    echo.
    echo [2/2] Informasi Alamat Akses untuk PC Client / HP:
    echo ================================================================
    echo.
    echo   Buka Google Chrome / Edge di PC Client atau HP, ketik URL ini:
    echo.
    echo   👉  http://192.168.100.14:5000
    echo.
    echo ================================================================
    echo Catatan: Pastikan PC Client / HP terhubung ke Wi-Fi / Router yang sama.
    echo.
    pause
) else (
    echo Meminta izin Administrator Windows (UAC)...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
)
