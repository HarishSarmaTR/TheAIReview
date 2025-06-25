# AI Review Tool - Version Information

## Version History

### V2.0.0 (Latest)
The latest version includes:
- Modern UI with customtkinter components
- Improved activity log with scrollable text widget
- "Clear" button for convenience
- Fixed Claude 4 Sonnet cost calculation
- Enhanced AI review prompt for more relevant feedback
- Improved icon and theme handling
- Better error handling and reporting

### v1.0.1
The original stable version includes:
- Basic tkinter UI
- Core functionality for:
  - GitHub authentication
  - OpenArena token management
  - Pull Request review
  - AI-powered code comments
- Token encryption for security

## How to Run Each Version

### Latest Version (V2.0.0)
```powershell
# Run from executable
.\dist\AIReviewTool_V2.0.0.exe

# Or run from source
.\run_ai_review.ps1
```

### Previous Version (v1.0.1)
```powershell
# Run from executable
.\dist\AIReviewTool_v1.0.1.exe

# Or run from source
.\run_v1.0.1.ps1
```

## Building From Source

### Latest Version (V2.0.0)
```powershell
.\build_executable.ps1
```

### Previous Version (v1.0.1)
```powershell
.\build_v1.0.1.ps1
```

## Differences Between Versions

### UI Changes
- V2.0.0 uses the modern customtkinter library for a more polished look
- v1.0.1 uses standard tkinter widgets

### Features
- V2.0.0 includes cost calculation for Claude 4 Sonnet
- V2.0.0 has an improved activity log for better user feedback
- V2.0.0 includes a "Clear" button for the activity log
- v1.0.1 has a simpler interface focused on core functionality

### System Requirements
Both versions have similar system requirements:
- Windows operating system
- Python 3.8 or higher (if running from source)
- Internet connection for GitHub and AI API access
