# Smart launcher for AI Review Tool
# This script checks available versions and launches the appropriate executable

function Find-ExecutableToRun {
    $v2Path = ".\dist\AIReviewTool_V2.0.0.exe"
    $v1Path = ".\dist\AIReviewTool_v1.0.1.exe"
    
    # First try latest version
    if (Test-Path $v2Path) {
        return @{
            Path = $v2Path
            Version = "V2.0.0"
        }
    }
    
    # Fall back to v1.0.1
    if (Test-Path $v1Path) {
        return @{
            Path = $v1Path
            Version = "v1.0.1"
        }
    }
    
    # No executable found, return nothing
    return $null
}

function Find-SourceToRun {
    $v2Source = ".\AIReview\AIReview.py"
    $v1Source = ".\AIReview\AIReview_v1.0.1.py"
    
    # First try latest version
    if (Test-Path $v2Source) {
        return @{
            Path = $v2Source
            Version = "V2.0.0"
        }
    }
    
    # Fall back to v1.0.1
    if (Test-Path $v1Source) {
        return @{
            Path = $v1Source
            Version = "v1.0.1"
        }
    }
    
    # No source found, return nothing
    return $null
}

# Display a menu and get user choice
function Show-VersionMenu {
    Clear-Host
    Write-Host "AI Review Tool - Version Selector" -ForegroundColor Cyan
    Write-Host "===============================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check if executables exist
    $v2ExeExists = Test-Path ".\dist\AIReviewTool_V2.0.0.exe"
    $v1ExeExists = Test-Path ".\dist\AIReviewTool_v1.0.1.exe"
    
    # Check if source files exist
    $v2SrcExists = Test-Path ".\AIReview\AIReview.py"
    $v1SrcExists = Test-Path ".\AIReview\AIReview_v1.0.1.py"
    
    Write-Host "Available versions:" -ForegroundColor Yellow
    
    # Display executable options
    if ($v2ExeExists) {
        Write-Host "1. Run V2.0.0 (Latest) - Executable" -ForegroundColor Green
    }
    if ($v1ExeExists) {
        Write-Host "2. Run v1.0.1 - Executable" -ForegroundColor Green
    }
    
    # Display source options
    if ($v2SrcExists) {
        Write-Host "3. Run V2.0.0 (Latest) - From Source" -ForegroundColor Magenta
    }
    if ($v1SrcExists) {
        Write-Host "4. Run v1.0.1 - From Source" -ForegroundColor Magenta
    }
    
    Write-Host "Q. Quit" -ForegroundColor Red
    Write-Host ""
    
    # Get user choice
    $choice = Read-Host "Please enter your choice"
    return $choice
}

# Main script
$choice = Show-VersionMenu

switch ($choice) {
    "1" {
        if (Test-Path ".\dist\AIReviewTool_V2.0.0.exe") {
            Write-Host "Starting AI Review Tool V2.0.0..." -ForegroundColor Green
            Start-Process ".\dist\AIReviewTool_V2.0.0.exe"
        }
        else {
            Write-Host "Error: Executable not found!" -ForegroundColor Red
        }
    }
    "2" {
        if (Test-Path ".\dist\AIReviewTool_v1.0.1.exe") {
            Write-Host "Starting AI Review Tool v1.0.1..." -ForegroundColor Green
            Start-Process ".\dist\AIReviewTool_v1.0.1.exe"
        }
        else {
            Write-Host "Error: Executable not found!" -ForegroundColor Red
        }
    }
    "3" {
        if (Test-Path ".\AIReview\AIReview.py") {
            Write-Host "Starting AI Review Tool V2.0.0 from source..." -ForegroundColor Green
            python ".\AIReview\AIReview.py"
        }
        else {
            Write-Host "Error: Source file not found!" -ForegroundColor Red
        }
    }
    "4" {
        if (Test-Path ".\AIReview\AIReview_v1.0.1.py") {
            Write-Host "Starting AI Review Tool v1.0.1 from source..." -ForegroundColor Green
            python ".\AIReview\AIReview_v1.0.1.py"
        }
        else {
            Write-Host "Error: Source file not found!" -ForegroundColor Red
        }
    }
    "Q" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    default {
        # Auto-detect and run the best available version
        $executable = Find-ExecutableToRun
        
        if ($executable) {
            Write-Host "Starting AI Review Tool $($executable.Version)..." -ForegroundColor Green
            Start-Process $executable.Path
        }
        else {
            $source = Find-SourceToRun
            
            if ($source) {
                Write-Host "Starting AI Review Tool $($source.Version) from source..." -ForegroundColor Green
                python $source.Path
            }
            else {
                Write-Host "Error: No version of AI Review Tool found!" -ForegroundColor Red
                exit 1
            }
        }
    }
}
