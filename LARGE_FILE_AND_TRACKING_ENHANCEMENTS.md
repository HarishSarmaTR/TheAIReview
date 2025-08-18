# AI Review Tool - Large File Support & Usage Tracking Enhancements

## Overview
This document outlines the enhancements made to fix issues with reviewing large files and new files, and to add comprehensive usage tracking capabilities.

## Issues Fixed

### 1. Large Files Issue
**Problem**: The tool was not able to review very large files effectively due to API limitations and processing constraints.

**Solution Implemented**:
- **File Size Detection**: Added checks for file size using GitHub API properties (`file.changes`, `file.additions`, `file.deletions`)
- **Chunking Strategy**: Implemented file chunking for files exceeding 500 changes
- **Configurable Limits**: 
  - MAX_CHANGES_PER_REVIEW = 500 (files with more changes get chunked)
  - Files with >2000 changes are skipped as too large
- **Enhanced Processing**: Large files are processed in smaller chunks with separate AI review calls
- **Chunk Reporting**: Each chunk is clearly marked in the output for better tracking

### 2. New Files Issue
**Problem**: New files were not being processed correctly, especially when they lacked proper patch data.

**Solution Implemented**:
- **Enhanced New File Detection**: Improved detection using multiple patterns:
  - `@@ -0,0` hunk headers
  - `new file mode` indicators
  - `index 0000000..` patterns
- **Content Retrieval**: For new files without patch data, retrieve content directly from GitHub API
- **Pseudo-Diff Creation**: Generate artificial diffs for new files to enable AI review
- **Size Limiting**: For very large new files (>500 lines), review only the first 500 lines
- **Better Logging**: Enhanced debug logging for new file processing

### 3. Enhanced Patch Processing
**Improvements Made**:
- **Robust Line Number Extraction**: Improved parsing of hunk headers with better regex patterns
- **Context Line Handling**: Better tracking of both old and new line numbers
- **Error Recovery**: Enhanced error handling for malformed patches
- **Whitespace Preservation**: Maintain original indentation and spacing in code snippets
- **Empty Line Handling**: Better processing of empty lines in patches

## Usage Tracking Enhancements

### 1. User Authentication & Access Control
- **SSO Integration**: Automatic detection of authenticated users from TokenExtraction
- **Admin Privileges**: Built-in admin user detection (configurable in `access_control.json`)
- **Session Management**: Comprehensive session tracking with start/end times
- **Access Logging**: All access attempts and permissions are logged

### 2. Comprehensive Activity Tracking
**What's Tracked**:
- User sessions (start/end times, duration)
- Code reviews performed (repository, PR number, file count)
- Comments generated and posted
- Costs and token usage
- System activities and errors
- Repository access patterns

**Data Collected**:
```json
{
  "session_id": "unique_identifier",
  "start_time": "2025-08-18T10:30:00",
  "end_time": "2025-08-18T10:45:00",
  "user_info": {
    "system_user": "6126175",
    "sso_user": "harish.sarma@thomsonreuters.com",
    "display_name": "Velavalapalli Harish Sarma"
  },
  "activities": [
    {
      "timestamp": "2025-08-18T10:32:00",
      "type": "CODE_REVIEW",
      "details": "Completed review - 5 files, 12 comments",
      "repo_name": "MyProject/API",
      "pr_number": "123"
    }
  ],
  "reviews_conducted": 1,
  "repositories_accessed": ["MyProject/API"],
  "pr_numbers_reviewed": ["123"]
}
```

### 3. Admin Reporting Interface
**New UI Features**:
- **Usage Report Button**: New "📊 Usage" button in the Results section (admin-only)
- **Comprehensive Reports**: Detailed usage statistics and user activity
- **Export Functionality**: Export reports to JSON format for external analysis
- **Real-time Data**: Live tracking during review sessions

**Report Contents**:
- Total sessions and unique users
- Repository access patterns
- User activity breakdown
- Recent session history
- Review statistics and trends

### 4. Access Control System
**File**: `access_control.json`
```json
{
  "admin_users": ["6126175", "harish.sarma@thomsonreuters.com"],
  "allowed_users": [],
  "require_approval": false,
  "usage_tracking": true,
  "detailed_logging": true
}
```

## Technical Implementation Details

### Files Modified:
1. **AIReview.py**:
   - Enhanced `get_modified_lines_from_patch()` function
   - Added file size checking and chunking logic
   - Improved new file handling
   - Added usage tracking integration
   - New UI elements for reporting

2. **simple_reviewer.py**:
   - Added `process_large_diff_in_chunks()` function
   - Enhanced prompts for large files and new files
   - Chunk processing with individual API calls

3. **usage_tracker.py**:
   - Enhanced reporting capabilities
   - Improved data structure for comprehensive tracking
   - Better JSON serialization handling

### Key Functions Added:
- `show_usage_report()`: Display admin usage reports
- `export_usage_report()`: Export data to JSON
- `process_large_diff_in_chunks()`: Handle large file chunking
- Enhanced session tracking and access control

## Usage Instructions

### For Regular Users:
1. **Large Files**: The tool now automatically handles large files by processing them in chunks
2. **New Files**: New files are automatically detected and reviewed appropriately
3. **No Changes Required**: All enhancements work transparently

### For Administrators:
1. **View Usage Reports**: Click the "📊 Usage" button in the Results section
2. **Export Data**: Use the export button in the report window to save data
3. **Access Control**: Modify `access_control.json` to manage user permissions
4. **Monitor Activity**: All user activity is automatically logged in `usage_log.json`

## Benefits

### Performance Improvements:
- ✅ Large files (>500 changes) now process successfully
- ✅ New files are properly detected and reviewed
- ✅ Chunking prevents API timeouts and memory issues
- ✅ Better error recovery and logging

### Usage Analytics:
- 📊 Complete visibility into tool usage patterns
- 👥 User activity tracking for management reporting
- 🔍 Repository access analytics
- 📈 Performance and cost tracking
- 🛡️ Access control and security monitoring

### User Experience:
- 🚀 Faster processing of large pull requests
- 📝 Better feedback for new file reviews
- 📊 Admin dashboard for usage insights
- 🔒 Secure access control system

## Configuration Options

### File Size Limits (in AIReview.py):
```python
MAX_CHANGES_PER_REVIEW = 500    # Chunk files larger than this
VERY_LARGE_FILE_LIMIT = 2000    # Skip files larger than this
NEW_FILE_REVIEW_LIMIT = 500     # Review first N lines of large new files
```

### Usage Tracking (in access_control.json):
- `usage_tracking`: Enable/disable tracking
- `detailed_logging`: Control log verbosity
- `admin_users`: List of admin user IDs/emails
- `require_approval`: Require admin approval for new users

## Security & Privacy

- All user data is stored locally
- No sensitive information is transmitted externally
- Admin controls for access management
- Session-based tracking with proper cleanup
- Configurable privacy levels

## Future Enhancements

Potential areas for future improvement:
1. **Cloud Analytics**: Integration with external analytics platforms
2. **Advanced Chunking**: Intelligent chunking based on code structure
3. **Performance Metrics**: Detailed performance tracking and optimization
4. **User Preferences**: Configurable review settings per user
5. **Batch Processing**: Support for reviewing multiple PRs simultaneously

---

**Version**: 2.1.3+
**Author**: Velavalapalli Harish Sarma
**Date**: August 18, 2025
