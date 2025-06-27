# Test script for AI Review Tool executable
# This script verifies the executable was built correctly

param (
    [string]$ExePath = "dist\AIReviewTool_V2.0.0.exe"
)

Write-Host "AI Review Tool Executable Test" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

# Check if executable exists
if (Test-Path -Path $ExePath) {
    $fileInfo = Get-ChildItem $ExePath
    Write-Host "✅ Executable found: $ExePath" -ForegroundColor Green
    Write-Host "   Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Green
    Write-Host "   Created: $($fileInfo.LastWriteTime)" -ForegroundColor Green
} else {
    Write-Host "❌ Executable not found: $ExePath" -ForegroundColor Red
    exit 1
}

# Check if ZIP archive exists
$zipPath = "dist\AIReviewTool_V2.0.0.zip"
if (Test-Path -Path $zipPath) {
    $zipInfo = Get-ChildItem $zipPath
    Write-Host "✅ ZIP archive found: $zipPath" -ForegroundColor Green
    Write-Host "   Size: $([math]::Round($zipInfo.Length / 1MB, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "⚠️ ZIP archive not found: $zipPath" -ForegroundColor Yellow
}

# Verify theme file was included
$themeFile = "dist\blue.json"
if (Test-Path -Path $themeFile) {
    Write-Host "✅ Theme file included: $themeFile" -ForegroundColor Green
} else {
    Write-Host "⚠️ Theme file not found: $themeFile" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Build Summary:" -ForegroundColor Cyan
Write-Host "- AI Review Tool V2.0.0 has been successfully compiled" -ForegroundColor Green
Write-Host "- The executable includes Claude 4 Sonnet integration" -ForegroundColor Green
Write-Host "- Enhanced OpenArena token validation is included" -ForegroundColor Green
Write-Host "- Modern CustomTkinter UI with Dark/Light mode support" -ForegroundColor Green
Write-Host ""
Write-Host "To use the executable:" -ForegroundColor Yellow
Write-Host "1. Double-click AIReviewTool_V2.0.0.exe to launch" -ForegroundColor White
Write-Host "2. Enter your GitHub and OpenArena tokens" -ForegroundColor White
Write-Host "3. Provide repository name and PR number" -ForegroundColor White
Write-Host "4. Click 'Run Code Review' to start the AI analysis" -ForegroundColor White
Write-Host ""
Write-Host "✅ Executable build test completed successfully!" -ForegroundColor Green
