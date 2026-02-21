param(
    [string]$RepoPath = (Split-Path -Parent $PSScriptRoot),
    [string]$Pattern = 'docs/*plan*.md',
    [string]$CommitPrefix = 'docs(plan): auto sync',
    [string]$LogPath = ''
)

$ErrorActionPreference = 'Stop'

function Write-Log {
    param([string]$Message)
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "[$ts] $Message"
    Write-Host $line
    if ($LogPath) {
        $dir = Split-Path -Parent $LogPath
        if ($dir -and -not (Test-Path $dir)) {
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
        }
        Add-Content -Path $LogPath -Value $line -Encoding UTF8
    }
}

function Invoke-Git {
    param([string[]]$Args)
    $output = & git @Args 2>&1
    $code = $LASTEXITCODE
    return [pscustomobject]@{ Output = $output; ExitCode = $code }
}

try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw 'Git not found. Please install Git and ensure it is in PATH.'
    }

    $repoResolved = Resolve-Path $RepoPath
    Push-Location $repoResolved

    $inside = Invoke-Git @('rev-parse', '--is-inside-work-tree')
    if ($inside.ExitCode -ne 0 -or ($inside.Output -join "`n").Trim() -ne 'true') {
        throw "Not a git repository: $repoResolved"
    }

    $status = Invoke-Git @('status', '--porcelain', '--', $Pattern)
    if ($status.ExitCode -ne 0) {
        throw "git status failed: $($status.Output -join '; ')"
    }

    $changed = ($status.Output | Where-Object { $_ -and $_.ToString().Trim() -ne '' })
    if (-not $changed -or $changed.Count -eq 0) {
        Write-Log "No changes for pattern '$Pattern'."
        exit 0
    }

    $add = Invoke-Git @('add', '--', $Pattern)
    if ($add.ExitCode -ne 0) {
        throw "git add failed: $($add.Output -join '; ')"
    }

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $message = "${CommitPrefix}: $timestamp"
    $commit = Invoke-Git @('commit', '-m', $message)
    if ($commit.ExitCode -ne 0) {
        $commitText = ($commit.Output -join "`n")
        if ($commitText -match 'nothing to commit') {
            Write-Log 'Nothing to commit after add.'
            exit 0
        }
        throw "git commit failed: $commitText"
    }

    $branch = Invoke-Git @('rev-parse', '--abbrev-ref', 'HEAD')
    if ($branch.ExitCode -ne 0) {
        throw "Unable to get current branch: $($branch.Output -join '; ')"
    }
    $currentBranch = ($branch.Output -join '').Trim()

    $push = Invoke-Git @('push', 'origin', $currentBranch)
    if ($push.ExitCode -ne 0) {
        throw "git push failed: $($push.Output -join '; ')"
    }

    Write-Log "Pushed commit to origin/$currentBranch."
    exit 0
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
}
finally {
    Pop-Location -ErrorAction SilentlyContinue
}

