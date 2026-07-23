@echo off
setlocal enabledelayedexpansion

:: Konfigurasi PATH
set PATH=C:\Program Files\nodejs;C:\Program Files\Git\cmd;%AppData%\npm;%PATH%

echo ============================================
echo [AI] Memulai Optimasi perakitan Gemma Gem...
echo ============================================

:: Cek keberadaan folder
if not exist "gemma-gem" (
    echo [ERROR] Folder gemma-gem tidak ditemukan!
    pause
    exit /b
)

cd gemma-gem

:: Cek pnpm
where pnpm >nul 2>nul
if %errorlevel% neq 0 (
    echo [AI] pnpm tidak ditemukan, mencoba install secara global...
    call npm install -g pnpm
)

echo [AI] Membersihkan cache dan menginstall dependensi...
call pnpm install

echo [AI] Mengupdate ONNX Runtime ke versi DEV (Lebih stabil untuk WebGPU)...
:: Menggunakan versi dev karena seringkali berisi fix terbaru untuk 'Device Lost' pada WebGPU
call pnpm add onnxruntime-web@dev

echo [AI] Membangun Ekstensi (Mode Produksi)...
call pnpm build

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo [AI] SELESAI! Folder rakitan: gemma-gem\.output
    echo [AI] Silahkan reload ekstensi di Chrome.
    echo ============================================
) else (
    echo [ERROR] Build gagal. Silahkan cek pesan error di atas.
)

pause
endlocal
