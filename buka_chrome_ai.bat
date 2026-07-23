@echo off
echo [INFO] Menutup Chrome yang sedang berjalan...
taskkill /F /IM chrome.exe /T >nul 2>&1

echo [INFO] Menjalankan Chrome dengan fitur Gemma AI (Gema Gem) dipaksa aktif...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --enable-features=LogOnDeviceModelExecution,OptimizationGuideOnDeviceModel,PromptAPI,TranslationAPI --disable-features=OptimizationGuideModelDownloadingRequirement

echo [SUCCESS] Chrome berhasil dijalankan. 
echo [INFO] Silahkan buka chrome://components dan cek "Optimization Guide On Device Model"
pause
