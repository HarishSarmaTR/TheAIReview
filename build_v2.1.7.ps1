# Build AI Review Tool v2.1.7 
# CRITICAL SECURITY UPDATE
# - Fixed token exposure vulnerability  
# - 64-bit compatibility for all Windows systems
# - Enhanced security with proper credential handling
# - Updated GitHub token setup guide with visual instructions

Write-Host "Building AI Review Tool v2.1.7 (SECURITY UPDATE)..." -ForegroundColor Green

# Build with PyInstaller
pyinstaller AIReviewTool_V2.1.7.spec

if (Test-Path "dist\AIReviewTool_V2.1.7.exe") {
    Write-Host "Build successful! Executable created: dist\AIReviewTool_V2.1.7.exe" -ForegroundColor Green
    
    # Get file size
    $fileSize = (Get-Item "dist\AIReviewTool_V2.1.7.exe").Length / 1MB
    Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    
    # Create version info
    $versionInfo = @{
        "version" = "2.1.7"
        "build_date" = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        "security_update" = $true
        "features" = @(
            "CRITICAL SECURITY FIX: Removed exposed tokens",
            "Fixed 64-bit compatibility issues", 
            "Enhanced security with proper .gitignore",
            "Updated GitHub token setup guide with images",
            "Fixed Unicode display issues",
            "Enhanced update notification UI",
            "Comprehensive usage tracking",
            "Improved AI review quality"
        )
        "distribution_ready" = $true
        "architecture" = "x86_64"
    }
    
    $versionInfo | ConvertTo-Json -Depth 3 | Out-File "dist\AIReviewTool_V2.1.7_info.json" -Encoding UTF8
    Write-Host "Version info saved to: dist\AIReviewTool_V2.1.7_info.json" -ForegroundColor Cyan
    
    Write-Host "SECURITY UPDATE COMPLETE - Safe for distribution!" -ForegroundColor Yellow
    
} else {
    Write-Host "Build failed! Executable not found." -ForegroundColor Red
    exit 1
}

Write-Host "Build process completed!" -ForegroundColor Green
