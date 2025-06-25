# AI Review Tool - Building & Backup Process

## Overview

This document explains the build process for the AI Review Tool executable and the backup mechanism that preserves previous versions.

## Build Scripts

### 1. `build_executable.ps1`

This PowerShell script builds the AI Review Tool executable using PyInstaller with the appropriate configurations.

**Usage:**
```powershell
.\build_executable.ps1 [-Version "V2.0.0"]
```

- `-Version`: Specifies the version for the executable name (default: "V2.0.0")

**What it does:**
1. Calls `backup_executable.ps1` to backup any existing executable
2. Runs PyInstaller to build a new executable
3. Creates a ZIP archive of the executable
4. Cleans up temporary build files
5. Preserves the `.spec` file for future builds

### 2. `backup_executable.ps1`

This script manages backup copies of the executable to ensure previous versions are preserved.

**Usage:**
```powershell
.\backup_executable.ps1 [-BuildVersion "V2.0.0"] [-LocalBuild]
```

- `-BuildVersion`: Specifies the version for the executable name (default: "V2.0.0")
- `-LocalBuild`: When specified, backs up the ZIP file as well as the executable

**What it does:**
1. Creates a `backup` folder inside the `dist` directory if it doesn't exist
2. If an executable exists, copies it to the backup folder with a timestamp
3. Retains only the most recent backup (plus the newly created one)
4. Optionally backs up the ZIP file for local builds

### 3. `cleanup.ps1`

The cleanup script has been modified to preserve the backup folder when cleaning up the workspace.

## GitHub Actions Workflow

The GitHub Actions workflow (`python-app.yml`) has been updated to include backup functionality:

1. Creates the necessary folder structure
2. Backs up any existing executable before building a new one
3. Ensures that the `blue.json` theme file is included in the build
4. Retains only the most recent backup

## PyInstaller Configuration

The PyInstaller spec file (`AIReviewTool_V2.0.0.spec`) has been updated to include the `blue.json` theme file, which prevents the `FileNotFoundError` that was occurring previously.

## Backup Location

Backups are stored in the `dist/backup` directory with a timestamp in the filename:
```
dist/backup/AIReviewTool_backup_YYYYMMDD-HHMMSS.exe
```

Only the most recent backup is kept to avoid accumulating too many files.

## Running the Application

Once built, you can run the application directly from the executable:
```
dist/AIReviewTool_V2.0.0.exe
```

Or use the provided PowerShell script:
```powershell
.\run_ai_review.ps1
```
