[CmdletBinding()]
param(
    [switch]$RunLocalDatabaseMigration,
    [switch]$SkipFrontend
)

$ErrorActionPreference = "Continue"
$results = [System.Collections.Generic.List[object]]::new()
$repoRoot = Split-Path -Parent $PSScriptRoot

function Invoke-ValidationStep {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )
    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    try {
        & $Command
        $code = $LASTEXITCODE
        if ($null -eq $code) { $code = 0 }
    }
    catch {
        Write-Host $_ -ForegroundColor Red
        $code = 1
    }
    $status = if ($code -eq 0) { "PASS" } else { "FAIL" }
    $results.Add([pscustomobject]@{ Check = $Name; Status = $status; ExitCode = $code })
    Write-Host "$status (exit $code): $Name" -ForegroundColor $(if ($code -eq 0) { "Green" } else { "Red" })
}

Push-Location $repoRoot
try {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) { Write-Error "Python 3.11+ was not found on PATH."; exit 2 }
    if (-not $SkipFrontend) {
        $npm = Get-Command npm -ErrorAction SilentlyContinue
        if (-not $npm) { Write-Error "Node.js/npm was not found on PATH."; exit 2 }
    }

    Push-Location (Join-Path $repoRoot "backend")
    try {
        Invoke-ValidationStep "Backend syntax compilation" { python -m compileall -q app migrations tests }
        Invoke-ValidationStep "Backend pytest" { python -m pytest }
        Invoke-ValidationStep "Backend Ruff" { python -m ruff check app tests migrations }
        if ($RunLocalDatabaseMigration) {
            Invoke-ValidationStep "Alembic upgrade head (local synthetic maalenex_dev only)" { python -m alembic upgrade head }
        } else {
            $results.Add([pscustomobject]@{ Check = "Alembic upgrade head"; Status = "NOT RUN (opt-in)"; ExitCode = $null })
        }
    }
    finally { Pop-Location }

    if (-not $SkipFrontend) {
        Push-Location (Join-Path $repoRoot "frontend")
        try {
            Invoke-ValidationStep "Frontend Vitest" { npm test }
            Invoke-ValidationStep "Frontend TypeScript typecheck" { npm run typecheck }
            Invoke-ValidationStep "Frontend production build" { npm run build }
        }
        finally { Pop-Location }
    } else {
        $results.Add([pscustomobject]@{ Check = "Frontend verification"; Status = "NOT RUN (skipped)"; ExitCode = $null })
    }
}
finally { Pop-Location }

Write-Host "`n=== A3 validation summary ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize
$failed = @($results | Where-Object { $_.Status -eq "FAIL" })
if ($failed.Count -gt 0) {
    Write-Host "$($failed.Count) validation check(s) failed." -ForegroundColor Red
    exit 1
}
Write-Host "Validation finished. NOT RUN items remain unverified." -ForegroundColor Green
exit 0
