Start-Transcript -Path "e:\register.log" -Force

try {
    Write-Output "Attempting to create MariaDB service..."
    New-Service -Name "MariaDB" -BinaryPathName '"C:\Program Files\MariaDB 12.2\bin\mariadbd.exe" --defaults-file="C:\Program Files\MariaDB 12.2\data\my.ini" MariaDB' -StartupType Automatic -ErrorAction Stop
    Write-Output "Service created successfully!"
} catch {
    Write-Error "Failed to create service: $_"
}

try {
    Write-Output "Attempting to start MariaDB service..."
    Start-Service -Name "MariaDB" -ErrorAction Stop
    Write-Output "Service started successfully!"
} catch {
    Write-Error "Failed to start service: $_"
}

Stop-Transcript
