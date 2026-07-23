$actionSleep = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -Command `"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, `$false, `$false)`""
$triggerSleep = New-ScheduledTaskTrigger -Daily -At 18:30
Register-ScheduledTask -Action $actionSleep -Trigger $triggerSleep -TaskName "SF_AutoSleep" -Description "Otomatis masuk mode Sleep jam 18:30" -Force

$actionWake = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c exit"
$triggerWake = New-ScheduledTaskTrigger -Daily -At 07:30
$settingsWake = New-ScheduledTaskSettingsSet -WakeToRun
Register-ScheduledTask -Action $actionWake -Trigger $triggerWake -Settings $settingsWake -TaskName "SF_AutoWake" -Description "Otomatis bangun dari Sleep jam 07:30" -Force
