# Build script for AIReview v1.0.1
# This script builds the v1.0.1 version of the AIReview Tool from the archived code

# Set variables
$sourceFile = ".\AIReview\AIReview_v1.0.1.py"
$outputName = "AIReviewTool_v1.0.1"
$iconFile = ".\images\ai.ico"

# Ensure the dist directory exists
if (-not (Test-Path ".\dist")) {
    New-Item -Path ".\dist" -ItemType Directory
}

# Clean up any existing v1.0.1 files
if (Test-Path ".\dist\$outputName.exe") {
    Remove-Item ".\dist\$outputName.exe" -Force
}

if (Test-Path ".\dist\$outputName.zip") {
    Remove-Item ".\dist\$outputName.zip" -Force
}

# Create PyInstaller spec file for v1.0.1
$specContent = @"
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['AIReview\\AIReview_v1.0.1.py'],
    pathex=[],
    binaries=[],
    datas=[('images/*', 'images/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='$outputName',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='$iconFile',
)
"@

# Save the spec file
$specFile = "$outputName.spec"
Set-Content -Path $specFile -Value $specContent

# Run PyInstaller to build the executable
Write-Host "Building $outputName.exe from $sourceFile..." -ForegroundColor Green
pyinstaller $specFile --clean

# Check if build was successful
if (Test-Path ".\dist\$outputName.exe") {
    Write-Host "$outputName.exe was built successfully!" -ForegroundColor Green
    
    # Create a zip file of the executable
    Write-Host "Creating zip archive of the executable..." -ForegroundColor Green
    Compress-Archive -Path ".\dist\$outputName.exe" -DestinationPath ".\dist\$outputName.zip" -Force
    
    Write-Host "Build complete! Files are available at:" -ForegroundColor Cyan
    Write-Host "  - .\dist\$outputName.exe" -ForegroundColor White
    Write-Host "  - .\dist\$outputName.zip" -ForegroundColor White
} else {
    Write-Host "Build failed! $outputName.exe was not created." -ForegroundColor Red
}
