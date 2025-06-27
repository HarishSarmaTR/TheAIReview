# AI Review Tool V2.0.0 - Production Deployment Script
param (
    [string]$Version = "V2.0.0",
    [string]$DeploymentPath = "RELEASE"
)

Write-Host "AI Review Tool V2.0.0 - Production Deployment" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Create deployment directory
$deployDir = Join-Path (Get-Location) $DeploymentPath
if (Test-Path $deployDir) {
    Write-Host "Cleaning existing deployment directory..." -ForegroundColor Yellow
    Remove-Item $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir -Force | Out-Null
Write-Host "Created deployment directory: $deployDir" -ForegroundColor Green

# Copy executable and ZIP
Write-Host "Copying production files..." -ForegroundColor Yellow
$exePath = "dist\AIReviewTool_$Version.exe"
$zipPath = "dist\AIReviewTool_$Version.zip"

if (Test-Path $exePath) {
    Copy-Item $exePath -Destination $deployDir
    Write-Host "Copied executable: AIReviewTool_$Version.exe" -ForegroundColor Green
} else {
    Write-Host "ERROR: Executable not found: $exePath" -ForegroundColor Red
    exit 1
}

if (Test-Path $zipPath) {
    Copy-Item $zipPath -Destination $deployDir
    Write-Host "Copied ZIP archive: AIReviewTool_$Version.zip" -ForegroundColor Green
}

# Copy documentation
Write-Host "Copying documentation..." -ForegroundColor Yellow
Copy-Item "PRODUCTION_RELEASE_$Version.md" -Destination $deployDir -ErrorAction SilentlyContinue
Copy-Item "docs\user_guide.html" -Destination $deployDir -ErrorAction SilentlyContinue
Copy-Item "README.md" -Destination $deployDir -ErrorAction SilentlyContinue

# Copy images for user guide
if (Test-Path "images") {
    Copy-Item "images" -Destination $deployDir -Recurse
    Write-Host "Copied images directory for documentation" -ForegroundColor Green
}

# Create deployment info file
$deploymentInfo = @"
# AI Review Tool V2.0.0 - Production Deployment Package

## Package Contents
- AIReviewTool_V2.0.0.exe (Main executable)
- AIReviewTool_V2.0.0.zip (Archive version)
- PRODUCTION_RELEASE_V2.0.0.md (Release notes)
- user_guide.html (User documentation)
- images/ (Documentation images)

## Deployment Instructions
1. Download AIReviewTool_V2.0.0.exe
2. Run the executable (no installation required)
3. Follow the user guide for setup and configuration

## Status: READY FOR PRODUCTION
- Build completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Platform: Windows 64-bit
- Built by: Ultratax Team, 2025
"@

$deploymentInfo | Out-File -FilePath (Join-Path $deployDir "DEPLOYMENT_INFO.md") -Encoding UTF8
Write-Host "Created deployment information file" -ForegroundColor Green

# Display final summary
Write-Host ""
Write-Host "Production Deployment Package Ready!" -ForegroundColor Green
Write-Host "Deployment Path: $deployDir" -ForegroundColor White
Write-Host ""
Get-ChildItem $deployDir | ForEach-Object {
    $size = if ($_.PSIsContainer) { "DIR" } else { "$([math]::Round($_.Length / 1MB, 1)) MB" }
    Write-Host "   $($_.Name) ($size)" -ForegroundColor White
}
Write-Host ""
Write-Host "READY FOR LIVE PRODUCTION DEPLOYMENT!" -ForegroundColor Green
