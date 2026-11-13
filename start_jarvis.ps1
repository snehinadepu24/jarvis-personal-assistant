#!/usr/bin/env pwsh
# JARVIS Backend Startup Script

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "  JARVIS Backend Startup" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan

# Check if in correct directory
if (!(Test-Path "backend\server.py")) {
    Write-Host "`n✗ Error: Must run from jarvis-personal-assistant root directory" -ForegroundColor Red
    exit 1
}

# Step 1: Check virtual environment
Write-Host "`n[1] Checking virtual environment..." -ForegroundColor Green
if (!(Test-Path ".venv")) {
    Write-Host "    Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}
Write-Host "    ✓ Virtual environment exists" -ForegroundColor Green

# Step 2: Activate virtual environment
Write-Host "`n[2] Activating virtual environment..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1
Write-Host "    ✓ Activated" -ForegroundColor Green

# Step 3: Install dependencies (quick check)
Write-Host "`n[3] Verifying dependencies..." -ForegroundColor Green
$needsInstall = $false
try {
    python -c "import fastapi, uvicorn, comtypes, win32gui" 2>$null
    if ($LASTEXITCODE -ne 0) { $needsInstall = $true }
}
catch {
    $needsInstall = $true
}

if ($needsInstall) {
    Write-Host "    Installing missing dependencies..." -ForegroundColor Yellow
    pip install -q -r backend\requirements.txt
    Set-Location jarvis
    pip install -q -e .
    pip install -q comtypes==1.4.16 pywin32
    Set-Location ..
    python -c "import comtypes.client; comtypes.client.GetModule('UIAutomationCore.dll')" 2>$null
    Write-Host "    ✓ Dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "    ✓ All dependencies present" -ForegroundColor Green
}

# Step 4: Verify API key
Write-Host "`n[4] Checking Gemini API configuration..." -ForegroundColor Green
$checkApiKey = @"
from jarvis.config import Config
import os
Config.load()
key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
if key:
    print(f'    ✓ API Key configured: {key[:10]}...')
else:
    print('    ✗ API key not configured!')
    exit(1)
"@
python -c $checkApiKey

if ($LASTEXITCODE -ne 0) {
    Write-Host "    Add GEMINI_API_KEY to jarvis/.env file" -ForegroundColor Yellow
    exit 1
}

# Step 5: Start server
Write-Host "`n[5] Starting backend server with uvicorn..." -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

uvicorn backend.server:app --host 127.0.0.1 --port 8000 --reload
