param(
    [string]$RepoPath = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

$gitHooksDir = Join-Path $RepoPath ".git/hooks"
$sourceHook = Join-Path $RepoPath "githooks/pre-push"
$targetHook = Join-Path $gitHooksDir "pre-push"

if (-not (Test-Path $sourceHook)) {
    throw "Source hook not found: $sourceHook"
}
if (-not (Test-Path $gitHooksDir)) {
    throw "Git hooks directory not found: $gitHooksDir"
}

Copy-Item -Path $sourceHook -Destination $targetHook -Force
Write-Host "Installed pre-push hook: $targetHook"
Write-Host "It will run regression checks before each push."

