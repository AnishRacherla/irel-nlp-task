# Setup Script for Windows
# This script helps set up the environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  iREL Pedagogical Flow Extractor" -ForegroundColor Cyan
Write-Host "  Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check FFmpeg
Write-Host "`n[2/6] Checking FFmpeg installation..." -ForegroundColor Yellow
$ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ FFmpeg found: $($ffmpegVersion.Split([Environment]::NewLine)[0])" -ForegroundColor Green
} else {
    Write-Host "⚠ FFmpeg not found. Installing via Chocolatey..." -ForegroundColor Yellow
    Write-Host "  If Chocolatey is not installed, please install FFmpeg manually from:" -ForegroundColor Yellow
    Write-Host "  https://ffmpeg.org/download.html" -ForegroundColor Yellow
    
    $chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue
    if ($chocoInstalled) {
        choco install ffmpeg -y
    }
}

# Create virtual environment
Write-Host "`n[3/6] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n[4/6] Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host "`n[5/6] Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Setup .env file
Write-Host "`n[6/6] Setting up environment file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created from template" -ForegroundColor Green
    Write-Host "⚠ IMPORTANT: Edit .env and add your OpenAI API key!" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env and add your OPENAI_API_KEY" -ForegroundColor White
Write-Host "2. Edit config/config.yaml and add your 5 video URLs" -ForegroundColor White
Write-Host "3. Run: python main.py --process-all" -ForegroundColor White
Write-Host "`nFor help: python main.py --help" -ForegroundColor Cyan
Write-Host ""
