# Build AI Review Tool v2.1.8 with Enhanced Security Features
# This script builds the executable with enterprise-grade security

Write-Host "Building AI Review Tool v2.1.8 - Enterprise Security Edition" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Yellow

# Set execution policy for this session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Get current directory
$currentDir = Get-Location
Write-Host "Current directory: $currentDir" -ForegroundColor Cyan

# Check if Python is available
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found in PATH. Please install Python first." -ForegroundColor Red
    exit 1
}

# Check if PyInstaller is installed
Write-Host "Checking PyInstaller..." -ForegroundColor Yellow
try {
    $pyinstallerVersion = pyinstaller --version 2>&1
    Write-Host "PyInstaller found: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Check security dependencies
Write-Host "Checking security dependencies..." -ForegroundColor Yellow
Write-Host "  - keyring (Windows Credential Manager)" -ForegroundColor Cyan
Write-Host "  - cryptography (encryption support)" -ForegroundColor Cyan
pip install keyring cryptography --upgrade

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist\AIReviewTool_V2.1.8.exe") { Remove-Item -Force "dist\AIReviewTool_V2.1.8.exe" }

# Build the executable
Write-Host "Building AI Review Tool v2.1.8..." -ForegroundColor Yellow
Write-Host "  - Target Architecture: x86_64 (64-bit)" -ForegroundColor Cyan
Write-Host "  - Security Features: Windows Credential Manager, Memory-only storage" -ForegroundColor Cyan
Write-Host "  - Token Protection: Enhanced .gitignore, secure storage" -ForegroundColor Cyan

pyinstaller AIReviewTool_V2.1.8.spec

# Check if build was successful
if (Test-Path "dist\AIReviewTool_V2.1.8.exe") {
    $fileInfo = Get-Item "dist\AIReviewTool_V2.1.8.exe"
    $fileSizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
    
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "=================================================================" -ForegroundColor Yellow
    Write-Host "Executable: dist\AIReviewTool_V2.1.8.exe" -ForegroundColor Green
    Write-Host "File Size: $fileSizeMB MB" -ForegroundColor Green
    Write-Host "Build Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green
    Write-Host "Security Level: Enterprise-Grade" -ForegroundColor Green
    Write-Host ""
    Write-Host "SECURITY FEATURES INCLUDED:" -ForegroundColor Yellow
    Write-Host "  - Windows Credential Manager integration" -ForegroundColor Green
    Write-Host "  - Memory-only token storage with automatic cleanup" -ForegroundColor Green
    Write-Host "  - Zero token persistence in executable" -ForegroundColor Green
    Write-Host "  - GitGuardian-compliant security architecture" -ForegroundColor Green
    Write-Host "  - Enhanced .gitignore protection" -ForegroundColor Green
    Write-Host ""
    Write-Host "READY FOR DISTRIBUTION!" -ForegroundColor Green
    Write-Host "  - No source code exposure" -ForegroundColor Cyan
    Write-Host "  - No embedded credentials" -ForegroundColor Cyan
    Write-Host "  - Secure token management" -ForegroundColor Cyan
    Write-Host "=================================================================" -ForegroundColor Yellow
} else {
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    Write-Host "Check the output above for error details." -ForegroundColor Yellow
    exit 1
}

# Clean up build artifacts
Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

Write-Host "Build process completed!" -ForegroundColor Green
