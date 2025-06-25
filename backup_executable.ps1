# Backup Executable Script for AI Review Tool
# This script backs up the existing executable before a new build

param (
    [string]$BuildVersion = "V2.0.0",
    [switch]$LocalBuild = $false
)

Write-Host "AI Review Tool Executable Backup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Standard paths
$distFolder = Join-Path (Get-Location) "dist"
$exeFileName = "AIReviewTool_$BuildVersion.exe"
$zipFileName = "AIReviewTool_$BuildVersion.zip"
$backupFolder = Join-Path $distFolder "backup"

# Create backup folder if it doesn't exist
if (-not (Test-Path -Path $backupFolder)) {
    Write-Host "Creating backup folder at $backupFolder..." -ForegroundColor Yellow
    New-Item -Path $backupFolder -ItemType Directory -Force | Out-Null
    Write-Host "Backup folder created!" -ForegroundColor Green
}

# Backup executable if it exists
$exePath = Join-Path $distFolder $exeFileName
if (Test-Path -Path $exePath) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupExeName = "AIReviewTool_backup_${timestamp}.exe"
    $backupPath = Join-Path $backupFolder $backupExeName
    
    Write-Host "Backing up $exeFileName to $backupPath..." -ForegroundColor Yellow
    Copy-Item -Path $exePath -Destination $backupPath -Force
    Write-Host "Executable backup successful!" -ForegroundColor Green
    
    # Retain only the most recent backup (in addition to the current one we're creating)
    $backupFiles = Get-ChildItem -Path $backupFolder -Filter "AIReviewTool_backup_*.exe" | 
                   Sort-Object LastWriteTime -Descending | 
                   Select-Object -Skip 1  # Skip the most recent one
    
    if ($backupFiles.Count -gt 0) {
        foreach ($file in $backupFiles) {
            Write-Host "Removing older backup: $($file.Name)" -ForegroundColor Yellow
            Remove-Item -Path $file.FullName -Force
        }
    }
} else {
    Write-Host "No existing executable found at $exePath, skipping backup." -ForegroundColor Gray
}

# Also backup the zip file if it exists and we're doing a local build
if ($LocalBuild) {
    $zipPath = Join-Path $distFolder $zipFileName
    if (Test-Path -Path $zipPath) {
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $backupZipName = "AIReviewTool_backup_${timestamp}.zip"
        $backupZipPath = Join-Path $backupFolder $backupZipName
        
        Write-Host "Backing up $zipFileName to $backupZipPath..." -ForegroundColor Yellow
        Copy-Item -Path $zipPath -Destination $backupZipPath -Force
        Write-Host "ZIP backup successful!" -ForegroundColor Green
    } else {
        Write-Host "No existing ZIP found at $zipPath, skipping backup." -ForegroundColor Gray
    }
}

Write-Host "Backup process completed!" -ForegroundColor Green
