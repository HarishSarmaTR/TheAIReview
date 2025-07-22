# Build Any Version Script for AI Review Tool
# This script allows building any available version

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("v1.0.1", "V2.0.1", "V2.0.6", "V2.0.7", "V2.0.8", "V2.0.9")]
    [string]$Version
)

$ErrorActionPreference = "Stop"

Write-Host "AI Review Tool - Build Any Version" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Requested Version: $Version" -ForegroundColor Yellow
Write-Host ""

switch ($Version) {
    "v1.0.1" {
        Write-Host "Building v1.0.1 (Classic UI)..." -ForegroundColor Green
        if (Test-Path "build_v1.0.1.ps1") {
            & .\build_v1.0.1.ps1
        } elseif (Test-Path "AIReviewTool_v1.0.1.spec") {
            Write-Host "Using PyInstaller directly..." -ForegroundColor Yellow
            pyinstaller AIReviewTool_v1.0.1.spec
        } else {
            Write-Host "ERROR: v1.0.1 build files not found!" -ForegroundColor Red
            exit 1
        }
    }
    
    "V2.0.0" {
        Write-Host "Building V2.0.0 (Initial Modern UI)..." -ForegroundColor Green
        if (Test-Path "AIReviewTool_V2.0.0.spec") {
            Write-Host "Using PyInstaller with V2.0.0 spec..." -ForegroundColor Yellow
            pyinstaller AIReviewTool_V2.0.0.spec
        } else {
            Write-Host "ERROR: V2.0.0 spec file not found!" -ForegroundColor Red
            exit 1
        }
    }
    
    "V2.0.1" {
        Write-Host "Building V2.0.1 (Latest)..." -ForegroundColor Green
        if (Test-Path "build_v2.0.1.ps1") {
            & .\build_v2.0.1.ps1
        } elseif (Test-Path "AIReviewTool_V2.0.1.spec") {
            Write-Host "Using PyInstaller directly..." -ForegroundColor Yellow
            pyinstaller AIReviewTool_V2.0.1.spec
        } else {
            Write-Host "ERROR: V2.0.1 build files not found!" -ForegroundColor Red
            exit 1
        }
    }
    
    "V2.0.6" {
        Write-Host "Building V2.0.6 (Latest)..." -ForegroundColor Green
        if (Test-Path "build_v2.0.6.ps1") {
            & .\build_v2.0.6.ps1
        } elseif (Test-Path "AIReviewTool_V2.0.6.spec") {
            Write-Host "Using PyInstaller directly..." -ForegroundColor Yellow
            pyinstaller AIReviewTool_V2.0.6.spec
        } else {
            Write-Host "ERROR: V2.0.6 build files not found!" -ForegroundColor Red
            exit 1
        }
    }
    "V2.0.7" {
        Write-Host "Building V2.0.7 (Latest)..." -ForegroundColor Green
        if (Test-Path "build_v2.0.7.ps1") {
            & .\build_v2.0.7.ps1
        } elseif (Test-Path "AIReviewTool_V2.0.7.spec") {
            Write-Host "Using PyInstaller directly..." -ForegroundColor Yellow
            pyinstaller AIReviewTool_V2.0.7.spec
        } else {
            Write-Host "ERROR: V2.0.7 build files not found!" -ForegroundColor Red
            exit 1
        }
    }
    "V2.0.8" {
        Write-Host "Building V2.0.8 (Latest)..." -ForegroundColor Green
        if (Test-Path "build_v2.0.8.ps1") {
            & .\build_v2.0.8.ps1
        } elseif (Test-Path "AIReviewTool_V2.0.8.spec") {
            Write-Host "Using PyInstaller directly..." -ForegroundColor Yellow
            pyinstaller AIReviewTool_V2.0.8.spec
        } else {
            Write-Host "ERROR: V2.0.8 build files not found!" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "Build process completed for version $Version!" -ForegroundColor Green
Write-Host "Check the dist/ folder for the executable." -ForegroundColor Cyan
