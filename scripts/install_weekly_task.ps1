param(
    [string]$TaskName = "T-Report Weekly Send",
    [string]$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$RunAt = "09:00",
    [string]$PythonCommand = "py"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$runnerPath = Join-Path $ProjectDir "scripts\run_weekly_send.ps1"
$actionArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$runnerPath`" -ProjectDir `"$ProjectDir`" -PythonCommand `"$PythonCommand`""

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $actionArgs
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At $RunAt
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Builds and sends the weekly T-Report email package every Monday." `
    -Force | Out-Null

Write-Host "Scheduled task '$TaskName' was registered for Monday at $RunAt."
