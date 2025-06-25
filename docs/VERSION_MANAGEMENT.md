# Version Management for AI Review Tool

This document explains how to maintain multiple versions of the AI Review Tool in the repository.

## Available Versions

Currently, the following versions are available:

- **v2.0.0** - Latest version with modern UI, improved cost calculation, and other enhancements
- **v1.0.1** - Original stable version

## Versioning Approach

We maintain both source code and executables for each version:

1. **Source Code**:
   - Latest version is in `AIReview/AIReview.py`
   - Previous versions are archived as `AIReview/AIReview_v{VERSION}.py`

2. **Executables**:
   - Latest version is built as `dist/AIReviewTool_V2.0.0.exe`
   - Previous versions are available as `dist/AIReviewTool_v{VERSION}.exe`

## Building Different Versions

### For the latest version (v2.0.0):
```powershell
.\build_executable.ps1
```

### For v1.0.1:
```powershell
.\build_v1.0.1.ps1
```

## Adding a New Version

1. **Archive the current version**:
   - Rename the latest version to include its version number
   - Example: `AIReview.py` → `AIReview_v2.0.0.py`

2. **Create a new build script**:
   - Copy and modify `build_executable.ps1` to target the specific version
   - Example: `build_v3.0.0.ps1`

3. **Update version number**:
   - In the new main `AIReview.py` file, update the `APP_VERSION` variable
   - In the build script, update the output file name

4. **Document the version**:
   - Update this file to include the new version details

## GitHub Actions

The GitHub Actions workflow is configured to build the latest version automatically. If you need to build older versions, you can either:

1. Run the appropriate build script locally and upload the executable
2. Enhance the GitHub Actions workflow to build multiple versions in parallel

## Accessing Old Versions

Users can download specific versions from the releases page on GitHub. Each release includes:

- The version number in the release title
- The executable packaged as a ZIP file
- Release notes describing the changes/features

## Version Changelog

### v2.0.0
- Modern UI with improved activity log
- Added "Clear" button
- Fixed Claude 4 Sonnet cost calculation
- Enhanced AI review prompt for more relevant feedback
- Improved icon and theme handling
- Better error handling

### v1.0.1
- Original stable version
- Basic UI functionality
- GitHub PR review capabilities
- Basic cost calculation
- Token management and encryption
