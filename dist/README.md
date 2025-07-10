# AI Code Review Tool - Distribution Folder

This folder contains all built executables and distribution packages for the AI Code Review Tool.

## Available Releases

### V2.0.1 (Current) - July 10, 2025
- **Executable**: `AIReviewTool_V2.0.1.exe` (34.07 MB)
- **Archive**: `AIReviewTool_V2.0.1.zip` (33.7 MB)
- **Status**: ✅ Current Production Release
- **Features**: Enhanced AI settings, improved error handling, modern UI

### V2.0.0 - June 27, 2025
- **Executable**: `AIReviewTool_V2.0.0.exe` (35 MB)
- **Archive**: `AIReviewTool_V2.0.0.zip` (34 MB)
- **Status**: ✅ Stable (Superseded)
- **Features**: Initial modern UI, Claude 4 Sonnet integration

## Usage

### Run Latest Version:
```
.\AIReviewTool_V2.0.1.exe
```

### Run Previous Version:
```
.\AIReviewTool_V2.0.0.exe
```

## Backup System

The `backup/` folder contains automatic backups created during builds:
- Previous executables are automatically backed up before new builds
- Backup naming format: `AIReviewTool_backup_YYYYMMDD-HHMMSS.exe`
- Both .exe and .zip files are backed up

## File Structure
```
dist/
├── AIReviewTool_V2.0.1.exe    # Latest executable
├── AIReviewTool_V2.0.1.zip    # Latest archive
├── AIReviewTool_V2.0.0.exe    # Previous stable
├── AIReviewTool_V2.0.0.zip    # Previous archive
├── backup/                    # Automatic backups
│   ├── AIReviewTool_backup_*.exe
│   └── AIReviewTool_backup_*.zip
├── blue.json                  # Theme configuration
└── README.md                  # This file
```

## System Requirements

- **OS**: Windows 10/11 (64-bit)
- **Memory**: 100+ MB RAM
- **Disk**: 50+ MB free space
- **Network**: Internet connection for GitHub and OpenArena APIs
- **Dependencies**: None (all bundled in executable)

## Deployment

### Single Machine:
1. Copy the desired `.exe` file to target machine
2. Run directly - no installation required

### Enterprise Distribution:
1. Use the `.zip` archive for consistent deployments
2. Extract and run the executable
3. Share user guide from `docs/user_guide.html`

## Support

- **Documentation**: See `../docs/` folder
- **User Guide**: `../docs/user_guide.html`
- **Version History**: `../VERSION_HISTORY.md`
- **Build Instructions**: `../docs/BUILD_README.md`

---

**Note**: All executables are self-contained and require no additional Python installation.
