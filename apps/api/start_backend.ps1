Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Run from backend directory regardless of caller location
$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendDir

$rootDir = Resolve-Path (Join-Path $backendDir "..")
$venvDir = Join-Path $rootDir ".venv"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"

Write-Host "==============================================="
Write-Host "  InternAI Backend Bootstrap"
Write-Host "==============================================="
Write-Host "Backend: $backendDir"
Write-Host "Root:    $rootDir"
Write-Host ""

if (-not (Test-Path $pythonExe)) {
    Write-Host "[1/3] Creating virtual environment at $venvDir ..."
    python -m venv $venvDir
}
else {
    Write-Host "[1/3] Virtual environment found."
}

Write-Host "[2/3] Installing/upgrading backend requirements ..."
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r (Join-Path $backendDir "requirements.txt")

Write-Host "[3/3] Starting FastAPI server on http://127.0.0.1:8000 ..."
Write-Host ""
& $pythonExe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
