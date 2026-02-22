param(
    [string]$RepoPath = (Split-Path -Parent $PSScriptRoot),
    [string]$Rules = "rules_v1.xlsx",
    [string]$Cases = "test_samples/cases.regression.json",
    [string]$Output = "test_samples/last_eval_report.regression.json"
)

$ErrorActionPreference = "Stop"

Push-Location $RepoPath
try {
    python ".\scripts\evaluate_samples.py" --rules $Rules --cases $Cases --output $Output
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Write-Host "Regression run finished with failures. ExitCode=$exitCode"
    }

    $reportPath = Join-Path $RepoPath $Output
    if (Test-Path $reportPath) {
        Write-Host "Report ready: $reportPath"
    } else {
        Write-Host "Report not found: $reportPath"
    }

    exit $exitCode
}
finally {
    Pop-Location
}
