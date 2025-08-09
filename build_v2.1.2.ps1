# Build Executable Script for AI Review Tool
# This script builds the executable with PyInstaller and manages backups

param (
    [string]$Version = "V2.1.2"
)

$ErrorActionPreference = "Stop"
9
Write-Host "AI Review Tool $Version Builder" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Run backup script first to preserve existing executable
Write-Host "Backing up existing executable (if present)..." -ForegroundColor Yellow
& .\backup_executable.ps1 -BuildVersion $Version -LocalBuild
Write-Host "Backup completed!" -ForegroundColor Green

# Copy theme file to current directory for PyInstaller to find it more easily
Write-Host "Ensuring theme file is accessible..." -ForegroundColor Yellow
if (-not (Test-Path -Path "blue.json")) {
    if (Test-Path -Path "AIReview/blue.json") {
        Copy-Item -Path "AIReview/blue.json" -Destination "blue.json" -Force
        Write-Host "Copied theme file from AIReview directory to root directory" -ForegroundColor Green
    } else {
        Write-Host "Theme file already exists in root directory" -ForegroundColor Green
    }
}

# Build the executable with PyInstaller using the specific spec file
Write-Host "Building executable with PyInstaller..." -ForegroundColor Yellow

# First, copy the icon to the root directory for easier access
if (-not (Test-Path -Path "ai.ico")) {
    Copy-Item -Path "images/ai.ico" -Destination "ai.ico" -Force
    Write-Host "Copied icon file to root directory for easier access" -ForegroundColor Green
}

# Use the specific spec file for version 2.0.5
$specFile = "AIReviewTool_$Version.spec"

# Execute PyInstaller with the spec file
Try {
    Write-Host "Using spec file: $specFile" -ForegroundColor Cyan
    pyinstaller $specFile
    
    # Verify the executable was created
    $exePath = "dist/AIReviewTool_$Version.exe"
    if (Test-Path -Path $exePath) {
        Write-Host "Executable successfully created at $exePath" -ForegroundColor Green
        
        # Get file size
        $fileSize = (Get-Item $exePath).length
        $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
        Write-Host "File size: $fileSizeMB MB" -ForegroundColor Cyan
        
        # Manually ensure theme file is in the right location in the dist folder
        if (-not (Test-Path -Path "dist/blue.json")) {
            if (Test-Path -Path "blue.json") {
                Copy-Item -Path "blue.json" -Destination "dist/blue.json" -Force
                Write-Host "Copied theme file to dist directory" -ForegroundColor Green
            } else {
                Write-Host "Warning: blue.json not found for dist directory" -ForegroundColor Yellow
            }
        }
        
        # Create a ZIP file of the executable
        $zipPath = "dist/AIReviewTool_$Version.zip"
        Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
        # Include both the executable and the theme file in the ZIP
        Compress-Archive -Path @("$exePath", "dist/blue.json") -DestinationPath $zipPath -Force
        Write-Host "ZIP archive created at $zipPath" -ForegroundColor Green
        
        # Get ZIP file size
        $zipSize = (Get-Item $zipPath).length
        $zipSizeMB = [math]::Round($zipSize / 1MB, 2)
        Write-Host "ZIP size: $zipSizeMB MB" -ForegroundColor Cyan
        
        # Test the executable quickly
        Write-Host "Testing executable startup..." -ForegroundColor Yellow
        try {
            $testProcess = Start-Process -FilePath $exePath -ArgumentList "--help" -NoNewWindow -PassThru -Wait
            if ($testProcess.ExitCode -eq 0 -or $null -eq $testProcess.ExitCode) {
                Write-Host "Executable startup test: PASSED" -ForegroundColor Green
            } else {
                Write-Host "Executable startup test: WARNING (exit code $($testProcess.ExitCode))" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "Executable startup test: SKIPPED (GUI application)" -ForegroundColor Yellow
        }
        
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
    
    Write-Host ""
    Write-Host "Build process completed successfully!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "Version: $Version" -ForegroundColor Cyan
    Write-Host "Executable: $exePath" -ForegroundColor Cyan
    Write-Host "ZIP archive: $zipPath" -ForegroundColor Cyan
    Write-Host "File size: $fileSizeMB MB" -ForegroundColor Cyan
    Write-Host "ZIP size: $zipSizeMB MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Ready for deployment!" -ForegroundColor Green

} Catch {
    Write-Host "ERROR: Build process failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
