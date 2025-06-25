# Cleanup Script for AI Review Tool
# This script removes temporary files and build artifacts

Write-Host "AI Review Tool Workspace Cleanup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Function to safely remove items with confirmation
function Remove-ItemSafely {
    param (
        [string]$Path,
        [string]$ItemType
    )
    
    if (Test-Path -Path $Path) {
        Write-Host "Removing $ItemType at $Path..." -ForegroundColor Yellow
        Remove-Item -Path $Path -Recurse -Force
        Write-Host "Done!" -ForegroundColor Green
    } else {
        Write-Host "$ItemType at $Path does not exist, skipping..." -ForegroundColor Gray
    }
}

# Clean up build artifacts
Remove-ItemSafely -Path "dist" -ItemType "Distribution folder"
Remove-ItemSafely -Path "build" -ItemType "Build folder"
Remove-ItemSafely -Path "AIReview/dist" -ItemType "AIReview distribution folder"
Remove-ItemSafely -Path "AIReview/build" -ItemType "AIReview build folder"

# Remove PyInstaller spec files
Get-ChildItem -Path "*.spec" | ForEach-Object {
    Write-Host "Removing spec file: $($_.FullName)" -ForegroundColor Yellow
    Remove-Item -Path $_.FullName -Force
    Write-Host "Done!" -ForegroundColor Green
}

# Clean Python cache files
Remove-ItemSafely -Path "__pycache__" -ItemType "Python cache"
Remove-ItemSafely -Path "AIReview/__pycache__" -ItemType "Python cache"
Remove-ItemSafely -Path "AIReview/core/__pycache__" -ItemType "Python cache"
Remove-ItemSafely -Path "AIReview/ui/__pycache__" -ItemType "Python cache"
Remove-ItemSafely -Path "AIReview/utils/__pycache__" -ItemType "Python cache"

# Remove test files
Remove-ItemSafely -Path "test_api.bat" -ItemType "Test batch file"

Write-Host "Cleanup completed successfully!" -ForegroundColor Green
