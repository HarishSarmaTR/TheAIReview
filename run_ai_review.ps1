# AI Review Tool Launcher
# This script runs the AIReview tool with the fixed version

Write-Host "Starting AIReview Tool..." -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptPath\AIReview"

# Run the AIReview.py file
python AIReview.py

Write-Host "=" * 50 -ForegroundColor Green
Write-Host "AI Review Tool session ended." -ForegroundColor Green
