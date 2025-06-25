# Build Executable Script for AI Review Tool
# This script builds the executable with PyInstaller and manages backups

param (
    [string]$Version = "V2.0.0"
)

$ErrorActionPreference = "Stop"

Write-Host "AI Review Tool Builder" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan

# Run backup script first to preserve existing executable
Write-Host "Backing up existing executable (if present)..." -ForegroundColor Yellow
& .\backup_executable.ps1 -BuildVersion $Version -LocalBuild
Write-Host "Backup completed!" -ForegroundColor Green

# Build the executable with PyInstaller
Write-Host "Building executable with PyInstaller..." -ForegroundColor Yellow
$pyinstallerArgs = @(
    "--name", "AIReviewTool_$Version",
    "--onefile",
    "--windowed",
    "--icon=images/ai.ico",
    "--add-data", "images/TR.png;images",
    "--add-data", "images/logo.png;images",
    "--add-data", "AIReview/blue.json;AIReview",
    "AIReview/AIReview.py"
)

# Execute PyInstaller
Try {
    pyinstaller @pyinstallerArgs
    
    # Verify the executable was created
    $exePath = "dist/AIReviewTool_$Version.exe"
    if (Test-Path -Path $exePath) {
        Write-Host "Executable successfully created at $exePath" -ForegroundColor Green
        
        # Create a ZIP file of the executable
        $zipPath = "dist/AIReviewTool_$Version.zip"
        Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
        Compress-Archive -Path $exePath -DestinationPath $zipPath -Force
        Write-Host "ZIP archive created at $zipPath" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Executable was not created at $exePath" -ForegroundColor Red
        exit 1
    }
    
    # Clean up build artifacts
    Write-Host "Cleaning up build artifacts..." -ForegroundColor Yellow
    if (Test-Path -Path "build") {
        Remove-Item -Path "build" -Recurse -Force
    }
    # Keep the spec file for future builds
    
    Write-Host "Build process completed successfully!" -ForegroundColor Green
    Write-Host "Executable: $exePath"
    Write-Host "ZIP archive: $zipPath"

} Catch {
    Write-Host "ERROR: Build process failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
