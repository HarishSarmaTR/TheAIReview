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

# Copy theme file to current directory for PyInstaller to find it more easily
Write-Host "Ensuring theme file is accessible..." -ForegroundColor Yellow
if (-not (Test-Path -Path "blue.json")) {
    Copy-Item -Path "AIReview/blue.json" -Destination "blue.json" -Force
    Write-Host "Copied theme file to root directory" -ForegroundColor Green
}

# Build the executable with PyInstaller
Write-Host "Building executable with PyInstaller..." -ForegroundColor Yellow

# First, copy the icon to the root directory for easier access
if (-not (Test-Path -Path "ai.ico")) {
    Copy-Item -Path "images/ai.ico" -Destination "ai.ico" -Force
    Write-Host "Copied icon file to root directory for easier access" -ForegroundColor Green
}

$pyinstallerArgs = @(
    "--name", "AIReviewTool_$Version",
    "--onefile",
    "--windowed",
    "--icon=ai.ico",  # Use the copied icon in root for better reliability
    "--add-data", "images/ai.ico;images",  # Include the icon in the images folder
    "--add-data", "ai.ico;.",  # Also include at root
    "--add-data", "images;images",  # Include ALL image files and subdirectories
    "--add-data", "AIReview/blue.json;AIReview", 
    "--add-data", "AIReview/blue.json;.",  # Also include at the root level for compatibility
    "--add-data", "docs;docs",  # Include ALL files in the docs directory
    "AIReview/AIReview.py"
)

# Execute PyInstaller
Try {
    pyinstaller @pyinstallerArgs
    
    # Verify the executable was created
    $exePath = "dist/AIReviewTool_$Version.exe"
    if (Test-Path -Path $exePath) {
        Write-Host "Executable successfully created at $exePath" -ForegroundColor Green
        
        # Manually ensure theme file is in the right location in the dist folder
        if (-not (Test-Path -Path "dist/blue.json")) {
            Copy-Item -Path "AIReview/blue.json" -Destination "dist/blue.json" -Force
            Write-Host "Copied theme file to dist directory" -ForegroundColor Green
        }
        
        # Create a ZIP file of the executable
        $zipPath = "dist/AIReviewTool_$Version.zip"
        Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
        # Include both the executable and the theme file in the ZIP
        Compress-Archive -Path @("$exePath", "dist/blue.json") -DestinationPath $zipPath -Force
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
