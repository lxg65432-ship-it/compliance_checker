param(
    [string]$RepoPath = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

Push-Location $RepoPath
try {
    Write-Host "[pre-push] Running regression suite..."
    python ".\scripts\evaluate_samples.py" `
        --rules "rules_v1.xlsx" `
        --cases "test_samples/cases.regression.json" `
        --output "test_samples/last_eval_report.regression.json"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[pre-push] Regression failed. Push blocked."
        exit 1
    }

    Write-Host "[pre-push] Regression passed. Push allowed."
    exit 0
}
finally {
    Pop-Location
}

