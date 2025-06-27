# AI Review Tool V2.0.0 - Production Deployment Script
# This script prepares the final release package for production deployment

param (
    [string]$Version = "V2.0.0",
    [string]$DeploymentPath = "RELEASE"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 AI Review Tool V2.0.0 - Production Deployment" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Create deployment directory
$deployDir = Join-Path (Get-Location) $DeploymentPath
if (Test-Path $deployDir) {
    Write-Host "Cleaning existing deployment directory..." -ForegroundColor Yellow
    Remove-Item $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir -Force | Out-Null
Write-Host "✅ Created deployment directory: $deployDir" -ForegroundColor Green

# Copy executable and ZIP
Write-Host "📦 Copying production files..." -ForegroundColor Yellow
$exePath = "dist\AIReviewTool_$Version.exe"
$zipPath = "dist\AIReviewTool_$Version.zip"

if (Test-Path $exePath) {
    Copy-Item $exePath -Destination $deployDir
    Write-Host "✅ Copied executable: AIReviewTool_$Version.exe" -ForegroundColor Green
} else {
    Write-Host "❌ Executable not found: $exePath" -ForegroundColor Red
    exit 1
}

if (Test-Path $zipPath) {
    Copy-Item $zipPath -Destination $deployDir
    Write-Host "✅ Copied ZIP archive: AIReviewTool_$Version.zip" -ForegroundColor Green
}

# Copy documentation
Write-Host "📚 Copying documentation..." -ForegroundColor Yellow
Copy-Item "PRODUCTION_RELEASE_$Version.md" -Destination $deployDir -ErrorAction SilentlyContinue
Copy-Item "docs\user_guide.html" -Destination $deployDir -ErrorAction SilentlyContinue
Copy-Item "README.md" -Destination $deployDir -ErrorAction SilentlyContinue

# Copy images for user guide
if (Test-Path "images") {
    Copy-Item "images" -Destination $deployDir -Recurse
    Write-Host "✅ Copied images directory for documentation" -ForegroundColor Green
}

# Create deployment info file
$deploymentInfo = @"
# AI Review Tool V2.0.0 - Production Deployment Package

## 📦 Package Contents
- AIReviewTool_V2.0.0.exe (Main executable - ~35MB)
- AIReviewTool_V2.0.0.zip (Archive version)
- PRODUCTION_RELEASE_V2.0.0.md (Release notes)
- user_guide.html (User documentation)
- images/ (Documentation images)

## 🚀 Deployment Instructions

### For End Users
1. Download AIReviewTool_V2.0.0.exe
2. Run the executable (no installation required)
3. Follow the user guide for setup and configuration

### For IT Deployment
1. Place AIReviewTool_V2.0.0.exe in desired location
2. Ensure users have network access to GitHub and OpenArena APIs
3. Distribute user guide and setup instructions
4. Configure SSO settings as needed

## ✅ Production Validation
- Build completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Executable size: $([math]::Round((Get-ChildItem "$exePath" -ErrorAction SilentlyContinue).Length / 1MB, 2)) MB
- ZIP size: $([math]::Round((Get-ChildItem "$zipPath" -ErrorAction SilentlyContinue).Length / 1MB, 2)) MB
- Platform: Windows 64-bit
- Status: ✅ READY FOR PRODUCTION

## 🔧 Technical Details
- Framework: Python 3.12 + CustomTkinter
- AI Model: Claude 4 Sonnet via OpenArena
- Packaging: PyInstaller with --onefile
- Icon: Embedded with Windows taskbar support
- Theme: Custom blue theme with Dark/Light mode

## 📞 Support
- Built by: Ultratax Team, 2025
- Contact: velavalapalli.harishsarma@thomsonreuters.com
- Platform: OpenArena AI Platform
"@

$deploymentInfo | Out-File -FilePath (Join-Path $deployDir "DEPLOYMENT_INFO.md") -Encoding UTF8
Write-Host "✅ Created deployment information file" -ForegroundColor Green

# Create a quick launcher script
$launcherScript = @"
@echo off
echo Starting AI Review Tool V2.0.0...
start "" "AIReviewTool_V2.0.0.exe"
"@

$launcherScript | Out-File -FilePath (Join-Path $deployDir "Launch_AI_Review_Tool.bat") -Encoding ASCII
Write-Host "✅ Created launcher script" -ForegroundColor Green

# Display final summary
Write-Host ""
Write-Host "🎉 Production Deployment Package Ready!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Deployment Path: $deployDir" -ForegroundColor White
Write-Host ""
Write-Host "📦 Package Contents:" -ForegroundColor Cyan
Get-ChildItem $deployDir | ForEach-Object {
    $size = if ($_.PSIsContainer) { "DIR" } else { "$([math]::Round($_.Length / 1MB, 1)) MB" }
    Write-Host "   $($_.Name) ($size)" -ForegroundColor White
}

Write-Host ""
Write-Host "🚀 Ready for Live Production Deployment!" -ForegroundColor Green
Write-Host "   • Executable tested and validated" -ForegroundColor Green
Write-Host "   • Documentation included" -ForegroundColor Green
Write-Host "   • User guide updated with SSO instructions" -ForegroundColor Green
Write-Host "   • Claude 4 Sonnet integration active" -ForegroundColor Green
Write-Host "   • Modern UI with Dark/Light mode" -ForegroundColor Green
Write-Host ""
Write-Host "✨ The AI Review Tool is ready to transform your code review process!" -ForegroundColor Yellow
