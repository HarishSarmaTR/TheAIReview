# PowerShell script to build AI Review Tool V2.1.3
# This script compiles the Python application into a standalone executable

Write-Host "Building AI Review Tool V2.1.3..." -ForegroundColor Green
Write-Host "=" * 60

# Set version and build info
$VERSION = "2.1.3"
$BUILD_DATE = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$OUTPUT_NAME = "AIReviewTool_V$VERSION"

Write-Host "Build Information:" -ForegroundColor Cyan
Write-Host "   Version: $VERSION"
Write-Host "   Date: $BUILD_DATE"
Write-Host "   Output: $OUTPUT_NAME"
Write-Host ""

# Check if PyInstaller is installed
Write-Host "Checking PyInstaller..." -ForegroundColor Yellow
try {
    $pyinstallerVersion = python -m PyInstaller --version 2>$null
    Write-Host "   PyInstaller found: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "   PyInstaller not found. Installing..." -ForegroundColor Red
    python -m pip install pyinstaller
}

# Check if Python is available
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>$null
    Write-Host "   Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   Python not found. Please install Python 3.8+." -ForegroundColor Red
    exit 1
}

# Create build directory
Write-Host "Setting up build environment..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

# Build the executable
Write-Host "Building executable..." -ForegroundColor Yellow
Write-Host "   This may take several minutes..." -ForegroundColor Gray

$buildCommand = @(
    "python", "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--name", $OUTPUT_NAME,
    "--icon", "ai.ico",
    "--add-data", "blue.json;.",
    "--add-data", "ai.ico;.",
    "--add-data", "access_control.json;.",
    "--add-data", "ai_settings.json;.",
    "--hidden-import", "customtkinter",
    "--hidden-import", "tkinter",
    "--hidden-import", "requests",
    "--hidden-import", "json",
    "--hidden-import", "datetime",
    "--hidden-import", "threading",
    "--hidden-import", "webbrowser",
    "--hidden-import", "os",
    "--hidden-import", "sys",
    "--hidden-import", "getpass",
    "--hidden-import", "usage_tracker",
    "--clean",
    "AIReview\AIReview.py"
)

try {
    & $buildCommand[0] $buildCommand[1..($buildCommand.Length-1)]
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Build completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "   Build failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   Build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check if executable was created
$exePath = "dist\$OUTPUT_NAME.exe"
if (Test-Path $exePath) {
    $fileSize = (Get-Item $exePath).Length
    $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
    
    Write-Host "Build Success!" -ForegroundColor Green
    Write-Host "   Location: $exePath"
    Write-Host "   Size: $fileSizeMB MB"
    Write-Host ""
    
    # Create release package
    Write-Host "Creating release package..." -ForegroundColor Yellow
    
    # Copy to RELEASE folder
    if (!(Test-Path "RELEASE")) {
        New-Item -ItemType Directory -Path "RELEASE"
    }
    
    Copy-Item $exePath "RELEASE\$OUTPUT_NAME.exe" -Force
    
    # Create ZIP archive
    $zipPath = "RELEASE\$OUTPUT_NAME.zip"
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    
    # Create temporary folder for ZIP contents
    $tempFolder = "temp_release"
    if (Test-Path $tempFolder) {
        Remove-Item -Recurse -Force $tempFolder
    }
    New-Item -ItemType Directory -Path $tempFolder
    
    # Copy files to temp folder
    Copy-Item $exePath "$tempFolder\$OUTPUT_NAME.exe"
    Copy-Item "README.md" "$tempFolder\" -ErrorAction SilentlyContinue
    Copy-Item "RELEASE_SUMMARY_V$VERSION.md" "$tempFolder\" -ErrorAction SilentlyContinue
    Copy-Item "user_guide.html" "$tempFolder\" -ErrorAction SilentlyContinue
    
    # Create ZIP
    Compress-Archive -Path "$tempFolder\*" -DestinationPath $zipPath -Force
    Remove-Item -Recurse -Force $tempFolder
    
    $zipSize = (Get-Item $zipPath).Length
    $zipSizeMB = [math]::Round($zipSize / 1MB, 2)
    
    Write-Host "   Release package created:" -ForegroundColor Green
    Write-Host "      Executable: $OUTPUT_NAME.exe ($fileSizeMB MB)" -ForegroundColor Cyan
    Write-Host "      Archive: $OUTPUT_NAME.zip ($zipSizeMB MB)" -ForegroundColor Cyan
    Write-Host ""
    
    # Test the executable
    Write-Host "Testing executable..." -ForegroundColor Yellow
    try {
        $null = & $exePath --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   Executable test passed" -ForegroundColor Green
        } else {
            Write-Host "   Executable test returned code $LASTEXITCODE" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   Could not test executable (this is normal for GUI apps)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Build Complete!" -ForegroundColor Green
    Write-Host "=" * 60
    Write-Host "Build Summary:" -ForegroundColor Cyan
    Write-Host "   Version: $VERSION"
    Write-Host "   Build Date: $BUILD_DATE"
    Write-Host "   Executable: RELEASE\$OUTPUT_NAME.exe ($fileSizeMB MB)" -ForegroundColor Cyan
    Write-Host "   Archive: RELEASE\$OUTPUT_NAME.zip ($zipSizeMB MB)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Ready for deployment!" -ForegroundColor Green
    
} else {
    Write-Host "Build failed - executable not found!" -ForegroundColor Red
    exit 1
}

# Clean up build artifacts
Write-Host "Cleaning up..." -ForegroundColor Gray
Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
Remove-Item "$OUTPUT_NAME.spec" -ErrorAction SilentlyContinue

Write-Host "Done!" -ForegroundColor Green
