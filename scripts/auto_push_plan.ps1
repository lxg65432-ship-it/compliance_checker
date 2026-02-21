param(
    [string]$RepoPath = (Split-Path -Parent $PSScriptRoot),
    [string]$WatchRelativePath = 'docs',
    [string]$Pattern = 'docs/*plan*.md',
    [string]$CommitPrefix = 'docs(plan): auto sync',
    [int]$DebounceSeconds = 3
)

$ErrorActionPreference = 'Stop'

$watchPath = Join-Path $RepoPath $WatchRelativePath
if (-not (Test-Path $watchPath)) {
    throw "Watch path does not exist: $watchPath"
}

$stateDir = Join-Path $RepoPath '.codex-auto-push'
$lockFile = Join-Path $stateDir 'auto_push.lock'
$logFile = Join-Path $stateDir 'auto_push.log'
$triggerFile = Join-Path $stateDir 'last_trigger.txt'
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

$runner = Join-Path $PSScriptRoot 'auto_push_once.ps1'
if (-not (Test-Path $runner)) {
    throw "Missing script: $runner"
}

function Write-Log {
    param([string]$Message)
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "[$ts] $Message"
    Write-Host $line
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

function Should-HandleEvent {
    param([string]$FullPath)
    if (-not $FullPath) { return $false }
    $name = [System.IO.Path]::GetFileName($FullPath)
    if ($name -notmatch '(?i)plan') { return $false }
    if ($name -notmatch '(?i)\.md$') { return $false }
    return $true
}

function Enter-Lock {
    if (Test-Path $lockFile) { return $false }
    New-Item -ItemType File -Path $lockFile -Force | Out-Null
    return $true
}

function Exit-Lock {
    if (Test-Path $lockFile) {
        Remove-Item -Path $lockFile -Force -ErrorAction SilentlyContinue
    }
}

$fsw = New-Object System.IO.FileSystemWatcher
$fsw.Path = $watchPath
$fsw.Filter = '*.md'
$fsw.IncludeSubdirectories = $false
$fsw.EnableRaisingEvents = $true

$action = {
    param($sender, $eventArgs)

    $fullPath = $eventArgs.FullPath
    if (-not (Should-HandleEvent -FullPath $fullPath)) {
        return
    }

    $now = Get-Date
    $last = $null
    if (Test-Path $triggerFile) {
        $raw = Get-Content $triggerFile -ErrorAction SilentlyContinue
        if ($raw) {
            [datetime]::TryParse($raw, [ref]$last) | Out-Null
        }
    }
    if ($last -and (($now - $last).TotalSeconds -lt $DebounceSeconds)) {
        return
    }

    Set-Content -Path $triggerFile -Value $now.ToString('o') -Encoding UTF8

    if (-not (Enter-Lock)) {
        Write-Log 'Skip event because a push job is already running.'
        return
    }

    try {
        Write-Log "Detected change: $fullPath"
        & powershell -ExecutionPolicy Bypass -File $runner `
            -RepoPath $RepoPath `
            -Pattern $Pattern `
            -CommitPrefix $CommitPrefix `
            -LogPath $logFile
        if ($LASTEXITCODE -ne 0) {
            Write-Log "auto_push_once exited with code $LASTEXITCODE"
        }
    }
    finally {
        Exit-Lock
    }
}

$subs = @()
$subs += Register-ObjectEvent -InputObject $fsw -EventName Changed -Action $action
$subs += Register-ObjectEvent -InputObject $fsw -EventName Created -Action $action
$subs += Register-ObjectEvent -InputObject $fsw -EventName Renamed -Action $action

Write-Log "Auto push watcher started. Path=$watchPath, Pattern=$Pattern"

try {
    while ($true) {
        Wait-Event -Timeout 2 | Out-Null
    }
}
finally {
    foreach ($s in $subs) {
        Unregister-Event -SourceIdentifier $s.Name -ErrorAction SilentlyContinue
    }
    $fsw.Dispose()
    Exit-Lock
    Write-Log 'Auto push watcher stopped.'
}
