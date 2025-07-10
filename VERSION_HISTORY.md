# AI Code Review Tool - Version History

## Version Release History

### V2.0.1 (Latest - July 10, 2025)
**Status**: ✅ Current Production Release

**Features:**
- Modern CustomTkinter UI with Dark/Light mode toggle
- Enhanced AI settings modal dialog with advanced configuration
- Improved token validation and error handling
- Real-time activity logging with timestamps
- Progress tracking with percentage display
- Recent repositories dropdown for quick access
- HTML report generation for offline viewing
- Comprehensive cost estimation and token tracking
- Claude 4 Sonnet integration via OpenArena

**Files:**
- `dist/AIReviewTool_V2.0.1.exe` (34.07 MB)
- `dist/AIReviewTool_V2.0.1.zip` (33.7 MB)
- `AIReviewTool_V2.0.1.spec`
- `build_v2.0.1.ps1`

**Build Info:**
- Built: July 10, 2025
- Python: 3.12.4
- PyInstaller: 6.12.0
- Dependencies: All bundled

---

### V2.0.0 (June 27, 2025)
**Status**: ✅ Stable Release (Superseded by V2.0.1)

**Features:**
- Initial CustomTkinter modern UI implementation
- Claude 4 Sonnet AI integration
- Basic activity logging and progress tracking
- GitHub PR integration with comment posting
- Token encryption and secure storage
- Cross-platform compatibility improvements

**Files:**
- `dist/AIReviewTool_V2.0.0.exe` (~35 MB)
- `dist/AIReviewTool_V2.0.0.zip` (~34 MB)
- `AIReviewTool_V2.0.0.spec`
- `RELEASE/` folder with complete production package

**Build Info:**
- Built: June 27, 2025
- Major UI overhaul from v1.0.1
- Enhanced error handling and retry logic

---

### v1.0.1 (June 2025)
**Status**: ✅ Legacy Stable (Classic UI)

**Features:**
- Original Tkinter-based UI
- Core GitHub PR review functionality
- Basic AI integration
- Token management
- Comment posting to GitHub PRs
- Simple cost calculation

**Files:**
- `AIReview_v1.0.1.py` (Source code preserved)
- `AIReviewTool_v1.0.1.spec`
- `build_v1.0.1.ps1`
- `run_v1.0.1.ps1`

**Build Info:**
- Classic Tkinter interface
- Simpler functionality
- Good for users who prefer traditional UI

---

## Migration Guide

### From v1.0.1 to V2.0.0+
- All token files are automatically migrated
- Recent repositories feature added
- Enhanced AI configuration available
- No manual migration needed

### From V2.0.0 to V2.0.1
- Settings migration automatic
- Enhanced AI configuration modal
- Improved error handling
- All previous features preserved

---

## Version Compatibility

| Feature | v1.0.1 | V2.0.0 | V2.0.1 |
|---------|--------|--------|--------|
| GitHub PR Review | ✅ | ✅ | ✅ |
| AI Integration | ✅ | ✅ | ✅ |
| Token Encryption | ✅ | ✅ | ✅ |
| Modern UI | ❌ | ✅ | ✅ |
| Dark/Light Mode | ❌ | ✅ | ✅ |
| Advanced AI Config | ❌ | ❌ | ✅ |
| Recent Repos | ❌ | ✅ | ✅ |
| HTML Reports | ❌ | ✅ | ✅ |
| Enhanced Logging | ❌ | ✅ | ✅ |

---

## Rollback Instructions

### To Rollback to V2.0.0:
```powershell
cd "C:\Users\6126175\TheAIReview\dist"
.\AIReviewTool_V2.0.0.exe
```

### To Rollback to v1.0.1:
```powershell
cd "C:\Users\6126175\TheAIReview"
python AIReview\AIReview_v1.0.1.py
```

---

## Build Instructions

### For V2.0.1:
```powershell
.\build_v2.0.1.ps1
```

### For V2.0.0:
```powershell
pyinstaller AIReviewTool_V2.0.0.spec
```

### For v1.0.1:
```powershell
.\build_v1.0.1.ps1
```

---

**Note**: All previous versions are maintained for compatibility and rollback purposes. The latest version (V2.0.1) is recommended for new deployments.
