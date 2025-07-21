# Build Executable Script for AI Review Tool v2.0.3
# This script builds the executable with PyInstaller and manages backups

param (
    [string]$Version = "V2.0.3"  # Default version, can be overridden
)

$ErrorActionPreference = "Stop"

Write-Host "AI Review Tool v2.0.3 Builder" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Run backup script first to preserve existing executable
Write-Host "Backing up existing executable (if present)..." -ForegroundColor Yellow
& .\backup_executable.ps1 -BuildVersion $Version -LocalBuild
Write-Host "Backup completed!" -ForegroundColor Green

# Verify required files exist before building
Write-Host "Verifying required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "AIReview/AIReview.py",
    "images/ai.ico",
    "docs"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path -Path $file)) {
        Write-Host "ERROR: Required file/directory not found: $file" -ForegroundColor Red
        exit 1
    }
}

# Check for blue.json in multiple locations
$blueJsonPath = $null
$possibleLocations = @(
    "blue.json",
    "AIReview/blue.json",
    "themes/blue.json"
)

foreach ($location in $possibleLocations) {
    if (Test-Path -Path $location) {
        $blueJsonPath = $location
        Write-Host "Found blue.json at: $location" -ForegroundColor Green
        break
    }
}

if (-not $blueJsonPath) {
    Write-Host "WARNING: blue.json theme file not found in any expected location" -ForegroundColor Yellow
    Write-Host "The application will use the default theme" -ForegroundColor Yellow
}

# Copy theme file to current directory for PyInstaller to find it more easily
Write-Host "Ensuring theme file is accessible..." -ForegroundColor Yellow
if ($blueJsonPath -and (-not (Test-Path -Path "blue.json"))) {
    Copy-Item -Path $blueJsonPath -Destination "blue.json" -Force
    Write-Host "Copied theme file from $blueJsonPath to root directory" -ForegroundColor Green
} elseif (Test-Path -Path "blue.json") {
    Write-Host "Theme file already exists in root directory" -ForegroundColor Green
}

# Copy icon to root directory for easier access
Write-Host "Preparing icon file..." -ForegroundColor Yellow
if (-not (Test-Path -Path "ai.ico")) {
    Copy-Item -Path "images/ai.ico" -Destination "ai.ico" -Force
    Write-Host "Copied icon file to root directory for easier access" -ForegroundColor Green
}

# Build the executable with PyInstaller
Write-Host "Building executable with PyInstaller..." -ForegroundColor Yellow

# Prepare PyInstaller arguments
$pyinstallerArgs = @(
    "--name", "AIReviewTool_$Version",
    "--onefile",
    "--windowed",
    "--icon=ai.ico",
    "--add-data", "images;images",
    "--add-data", "docs;docs"
)

# Add theme file if it exists
if (Test-Path -Path "blue.json") {
    $pyinstallerArgs += "--add-data", "blue.json;."
}

# Add the main Python file
$pyinstallerArgs += "AIReview/AIReview.py"

# Execute PyInstaller
Try {
    Write-Host "PyInstaller arguments: $($pyinstallerArgs -join ' ')" -ForegroundColor Cyan
    pyinstaller @pyinstallerArgs
    
    # Verify the executable was created
    $exePath = "dist/AIReviewTool_$Version.exe"
    if (Test-Path -Path $exePath) {
        Write-Host "Executable successfully created at $exePath" -ForegroundColor Green
        
        # Get file size
        $fileSize = (Get-Item $exePath).length
        $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
        Write-Host "File size: $fileSizeMB MB" -ForegroundColor Cyan
        
        # Manually ensure theme file is in the right location in the dist folder
        if ((Test-Path -Path "blue.json") -and (-not (Test-Path -Path "dist/blue.json"))) {
            Copy-Item -Path "blue.json" -Destination "dist/blue.json" -Force
            Write-Host "Copied theme file to dist directory" -ForegroundColor Green
        }
        
        # Create a ZIP file of the executable
        $zipPath = "dist/AIReviewTool_$Version.zip"
        Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
        
        # Prepare items for ZIP
        $zipItems = @($exePath)
        if (Test-Path -Path "dist/blue.json") {
            $zipItems += "dist/blue.json"
        }
        
        Compress-Archive -Path $zipItems -DestinationPath $zipPath -Force
        Write-Host "ZIP archive created at $zipPath" -ForegroundColor Green
        
        # Get ZIP file size
        $zipSize = (Get-Item $zipPath).length
        $zipSizeMB = [math]::Round($zipSize / 1MB, 2)
        Write-Host "ZIP size: $zipSizeMB MB" -ForegroundColor Cyan
        
        # Test the executable quickly
        Write-Host "Testing executable startup..." -ForegroundColor Yellow
        try {
            $testProcess = Start-Process -FilePath $exePath -ArgumentList "--version" -NoNewWindow -PassThru -Wait -ErrorAction SilentlyContinue
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
        
        # Check if there are any files in the dist directory
        if (Test-Path -Path "dist") {
            $distFiles = Get-ChildItem -Path "dist" -File
            if ($distFiles.Count -gt 0) {
                Write-Host "Files found in dist directory:" -ForegroundColor Yellow
                foreach ($file in $distFiles) {
                    Write-Host "  - $($file.Name)" -ForegroundColor Yellow
                }
            } else {
                Write-Host "No files found in dist directory" -ForegroundColor Red
            }
        } else {
            Write-Host "Dist directory was not created" -ForegroundColor Red
        }
        
        exit 1
    }
    
    # Clean up build artifacts
    Write-Host "Cleaning up build artifacts..." -ForegroundColor Yellow
    if (Test-Path -Path "build") {
        Remove-Item -Path "build" -Recurse -Force
    }
    
    # Clean up temporary files
    if (Test-Path -Path "ai.ico") {
        Remove-Item -Path "ai.ico" -Force
    }
    if (Test-Path -Path "blue.json" -and $blueJsonPath -ne "blue.json") {
        Remove-Item -Path "blue.json" -Force
    }
    
    Write-Host ""
    Write-Host "Build process completed successfully!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "Version: 2.0.3" -ForegroundColor Cyan
    Write-Host "Executable: $exePath" -ForegroundColor Cyan
    Write-Host "ZIP archive: $zipPath" -ForegroundColor Cyan
    Write-Host "File size: $fileSizeMB MB" -ForegroundColor Cyan
    Write-Host "ZIP size: $zipSizeMB MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Ready for deployment!" -ForegroundColor Green

} Catch {
    Write-Host "ERROR: Build process failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    # Show more detailed error information
    Write-Host "Full error details:" -ForegroundColor Red
    Write-Host $_.Exception.ToString() -ForegroundColor Red
    
    exit 1
}