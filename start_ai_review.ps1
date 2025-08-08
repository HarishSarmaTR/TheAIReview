# AI Review Tool Startup Script (PowerShell)
# Ensures the application runs from the correct directory

Write-Host "Starting AI Review Tool..." -ForegroundColor Green
Write-Host ""

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Navigate to the AIReview subdirectory
$AIReviewDir = Join-Path $ScriptDir "AIReview"
Set-Location $AIReviewDir

# Check if AIReview.py exists
$AIReviewScript = "AIReview.py"
if (-not (Test-Path $AIReviewScript)) {
    Write-Host "ERROR: AIReview.py not found in $(Get-Location)" -ForegroundColor Red
    Write-Host "Please ensure this script is in the correct directory." -ForegroundColor Red
    Write-Host "Expected file: $(Join-Path (Get-Location) $AIReviewScript)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Display current directory and file info
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host "Starting AIReview.py..." -ForegroundColor Green
Write-Host ""

# Start the application
try {
    python AIReview.py
} catch {
    Write-Host ""
    Write-Host "ERROR: Application failed to start" -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}

Write-Host ""
Write-Host "AI Review Tool has closed." -ForegroundColor Yellow
