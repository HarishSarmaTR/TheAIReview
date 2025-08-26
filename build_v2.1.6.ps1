# Build AI Review Tool v2.1.6
# This script builds the executable with all improvements including:
# - Fixed Unicode display issues
# - Enhanced update notification UI  
# - Separated Thomson Reuters/UltraTax branding
# - Resolved function naming conflicts
# - Eliminated "Line N/A" comments from reviews
# - Comprehensive usage tracking

Write-Host "Building AI Review Tool v2.1.6..." -ForegroundColor Green

# Build with PyInstaller
pyinstaller AIReviewTool_V2.1.6.spec

if (Test-Path "dist\AIReviewTool_V2.1.6.exe") {
    Write-Host "Build successful! Executable created: dist\AIReviewTool_V2.1.6.exe" -ForegroundColor Green
    
    # Get file size
    $fileSize = (Get-Item "dist\AIReviewTool_V2.1.6.exe").Length / 1MB
    Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    
    # Create version info
    $versionInfo = @{
        "version" = "2.1.6"
        "build_date" = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        "features" = @(
            "Fixed Unicode display issues",
            "Enhanced update notification UI",
            "Separated Thomson Reuters/UltraTax branding",
            "Resolved function naming conflicts",
            "Eliminated unwanted Line N/A comments",
            "Comprehensive usage tracking",
            "Improved AI review quality"
        )
    }
    
    $versionInfo | ConvertTo-Json -Depth 3 | Out-File "dist\AIReviewTool_V2.1.6_info.json" -Encoding UTF8
    Write-Host "Version info saved to: dist\AIReviewTool_V2.1.6_info.json" -ForegroundColor Cyan
    
} else {
    Write-Host "Build failed! Executable not found." -ForegroundColor Red
    exit 1
}

Write-Host "Build process completed!" -ForegroundColor Green
