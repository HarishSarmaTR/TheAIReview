# Run script for AIReview v1.0.1
# This script runs the v1.0.1 version of the AIReview Tool from the original code

Write-Host "Running AIReview Tool v1.0.1..." -ForegroundColor Green
Write-Host "This will launch the application directly from the source code." -ForegroundColor Yellow

# Set the current directory to the project root
$scriptPath = $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

# Change to the project directory
Set-Location $projectRoot

# Run the v1.0.1 version
python ./AIReview/AIReview_v1.0.1.py
