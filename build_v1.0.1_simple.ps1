# Simplified build script for v1.0.1
# This script builds the v1.0.1 executable directly

Write-Host "Building AIReviewTool_v1.0.1.exe..." -ForegroundColor Green

# Clean up any existing files
if (Test-Path ".\dist\AIReviewTool_v1.0.1.exe") {
    Remove-Item ".\dist\AIReviewTool_v1.0.1.exe" -Force
}

# Run PyInstaller directly
pyinstaller --onefile --windowed --icon="images/ai.ico" --name="AIReviewTool_v1.0.1" --add-data "images/ai.ico;images" --add-data "images/bot.JPG;images" "AIReview/AIReview_v1.0.1.py"

# Check if build was successful
if (Test-Path ".\dist\AIReviewTool_v1.0.1.exe") {
    Write-Host "Build successful! Executable is at dist\AIReviewTool_v1.0.1.exe" -ForegroundColor Green
    
    # Create ZIP file
    if (Test-Path ".\dist\AIReviewTool_v1.0.1.zip") {
        Remove-Item ".\dist\AIReviewTool_v1.0.1.zip" -Force
    }
    
    Compress-Archive -Path ".\dist\AIReviewTool_v1.0.1.exe" -DestinationPath ".\dist\AIReviewTool_v1.0.1.zip" -Force
    Write-Host "Created ZIP archive at dist\AIReviewTool_v1.0.1.zip" -ForegroundColor Green
} else {
    Write-Host "Build failed! Executable not created." -ForegroundColor Red
}
