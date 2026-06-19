# scripts/setup_kaggle.ps1 — Verify and guide Kaggle API token setup (Windows)
$ErrorActionPreference = "Stop"

$kaggleDir = Join-Path $env:USERPROFILE ".kaggle"
$kaggleJson = Join-Path $kaggleDir "kaggle.json"
$kaggleToken = Join-Path $kaggleDir "access_token"

Write-Host "=== Kaggle API Token Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if either token format exists
$jsonExists = Test-Path $kaggleJson
$tokenExists = Test-Path $kaggleToken

if ($jsonExists -or $tokenExists) {
    if ($jsonExists) {
        Write-Host "[OK] Kaggle token found at: $kaggleJson" -ForegroundColor Green
    }
    if ($tokenExists) {
        Write-Host "[OK] Kaggle access_token found at: $kaggleToken" -ForegroundColor Green
    }

    # Verify token works
    if (Get-Command kaggle -ErrorAction SilentlyContinue) {
        Write-Host ""
        Write-Host "Verifying API connection..."
        try {
            kaggle datasets list -s "chicago-crime" --max-size 1 2>$null | Select-Object -First 1
            Write-Host "[OK] Kaggle API connection verified" -ForegroundColor Green
        } catch {
            Write-Host "[WARN] Token exists but API call failed" -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "[WARN] kaggle CLI not installed" -ForegroundColor Yellow
        Write-Host "       Install: pip install kaggle" -ForegroundColor Yellow
    }
} else {
    Write-Host "[MISSING] No Kaggle token found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Option 1: KGAT Token (recommended)" -ForegroundColor White
    Write-Host "  1. Go to https://www.kaggle.com/settings" -ForegroundColor White
    Write-Host "  2. Under API, click 'Create New Token'" -ForegroundColor White
    Write-Host "  3. Run this command with your KGAT token:" -ForegroundColor White
    Write-Host ""
    Write-Host "     `$token = Read-Host -Prompt 'Enter your KGAT token'" -ForegroundColor Yellow
    Write-Host "     New-Item -ItemType Directory -Force -Path `"$kaggleDir`" | Out-Null" -ForegroundColor Yellow
    Write-Host "     `$token | Set-Content `"$kaggleToken`" -NoNewline" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 2: JSON Token" -ForegroundColor White
    Write-Host "  1. Go to https://www.kaggle.com/settings" -ForegroundColor White
    Write-Host "  2. Under API, click 'Create New Token'" -ForegroundColor White
    Write-Host "  3. Move kaggle.json to: $kaggleDir" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Ready for: make seed" -ForegroundColor Green
