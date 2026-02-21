param(
    [string]$TaskName = 'ComplianceChecker_AutoPushPlan',
    [string]$RepoPath = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot 'auto_push_plan.ps1'
if (-not (Test-Path $scriptPath)) {
    throw "Missing script: $scriptPath"
}

$arg = "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" -RepoPath `"$RepoPath`""
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arg
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings | Out-Null
Write-Host "Scheduled task '$TaskName' registered. It will start at logon."
Write-Host "Manual start: Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "Disable: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
