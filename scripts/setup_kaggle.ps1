# scripts/setup_kaggle.ps1 — Verify and guide Kaggle API token setup (Windows)
$ErrorActionPreference = "Stop"

$kaggleDir = Join-Path $env:USERPROFILE ".kaggle"
$kaggleJson = Join-Path $kaggleDir "kaggle.json"

Write-Host "=== Kaggle API Token Setup ===" -ForegroundColor Cyan
Write-Host ""

if (Test-Path $kaggleJson) {
    Write-Host "[OK] Kaggle token found at: $kaggleJson" -ForegroundColor Green

    # Verify token works
    if (Get-Command kaggle -ErrorAction SilentlyContinue) {
        Write-Host ""
        Write-Host "Verifying API connection..."
        try {
            kaggle datasets list -s "chicago-crime" --max-size 1 2>$null | Select-Object -First 1
            Write-Host "[OK] Kaggle API connection verified" -ForegroundColor Green
        } catch {
            Write-Host "[WARN] Token exists but API call failed — check kaggle.json contents" -ForegroundColor Yellow
            Write-Host "       Expected format: {`"username`": `"...`", `"key`": `"...`"}" -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "[WARN] kaggle CLI not installed" -ForegroundColor Yellow
        Write-Host "       Install: pip install kaggle" -ForegroundColor Yellow
    }
} else {
    Write-Host "[MISSING] No Kaggle token found at: $kaggleJson" -ForegroundColor Red
    Write-Host ""
    Write-Host "Setup instructions:" -ForegroundColor White
    Write-Host "  1. Go to https://www.kaggle.com/settings" -ForegroundColor White
    Write-Host "  2. Under 'API' section, click 'Create New Token'" -ForegroundColor White
    Write-Host "  3. Save the downloaded kaggle.json to:" -ForegroundColor White
    Write-Host "       $kaggleJson" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Or run in PowerShell:" -ForegroundColor White
    Write-Host "       mkdir -Force `"$kaggleDir`"" -ForegroundColor Yellow
    Write-Host "       '{`"username`": `"YOUR_USERNAME`", `"key`": `"YOUR_KEY`"}' | Set-Content `"$kaggleJson`" -Encoding UTF8" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Ready for: make seed" -ForegroundColor Green
