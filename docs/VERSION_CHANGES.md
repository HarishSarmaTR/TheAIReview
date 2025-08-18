# Multiple Versions Management - Changes Summary

## Changes Made

1. **Created Version-Specific Build Scripts**
   - `build_v1.0.1.ps1` - Full build script for v1.0.1 with PyInstaller spec file generation
   - `build_v1.0.1_simple.ps1` - Simplified direct build script for v1.0.1 

2. **Created Version Selection Tools**
   - `run_v1.0.1.ps1` - Script to run v1.0.1 directly from source
   - `run_ai_review_selector.ps1` - Interactive menu to select and run any available version

3. **Updated GitHub Actions Workflow**
   - Modified the CI/CD workflow to build both v1.0.1 and V2.0.0 executables
   - Updated artifact upload to include both versions
   - Updated release step to publish both versions in GitHub releases

4. **Created Documentation**
   - `VERSION_MANAGEMENT.md` - Explains the versioning approach and how to maintain multiple versions
   - `VERSION_INFO.md` - Details about each version and how to run them
   - Updated `README.md` to mention the multiple versions and the selector script

5. **Built Both Executable Versions**
   - Successfully built `AIReviewTool_V2.0.0.exe` and `AIReviewTool_v1.0.1.exe`
   - Created ZIP archives for both versions

## Available Versions

1. **V2.1.3 (Latest)**
   - **Enterprise Usage Tracking**: High-capacity monitoring system (10,000 sessions)
   - **Admin Management Tools**: CLI and GUI interfaces for admin management
   - **Monthly Archiving**: Intelligent data management with automatic archiving
   - **Dev Monitor Fixes**: Resolved "Usage tracking module not available" error
   - **Enhanced Security**: Admin-only visibility with stealth monitoring
   - **Business Intelligence**: Export-ready analytics and comprehensive reporting
   - **Automatic Backups**: Timestamped configuration backups for safety

2. **V2.1.2 (Previous)**
   - **Tool File Filtering**: Automatically skips tool files (`*/tool/*`, `*/tools/*`) from code review
   - **Code Snippet Integration**: HTML reports now include actual code snippets for each AI comment
   - **Enhanced AI Focus**: AI now focuses exclusively on modified lines rather than entire file context
   - **Improved File Processing Summary**: Detailed summary of why files were skipped with clear categories
   - **Better Line Number Detection**: Enhanced regex patterns for extracting line numbers from AI responses
   - **Visual Code Context**: Enhanced CSS styling for code snippets with proper formatting
   - **Precision Targeting**: Reduced noise by eliminating comments on unchanged surrounding code
   - **Enhanced Logging**: Clear indication when tool files are skipped with reasoning

2. **V2.1.1**
   - Enhanced UI with improved emoji integration throughout the interface
   - Fixed emoji display issues (replaced ?? placeholders with proper emojis)
   - Improved feedback window visibility and sizing (650x650 for better user experience)
   - Enhanced "Post comments to PR" checkbox with helpful description
   - Updated About section with structured content and professional formatting
   - Better tooltip explanations for user interface elements
   - All UI elements now display proper emojis for enhanced visual appeal
   - Refined Claude 4 Sonnet branding with elegant sparkles emoji

2. **V2.1.0**
   - Modern UI with customtkinter components
   - Enhanced background image and visual aesthetics
   - Improved activity log with timestamped entries and scrollable text widget
   - Progress bar with percentage display for better user feedback
   - "Clear" button that resets both activity log and review metrics
   - Fixed Claude 4 Sonnet cost calculation with detailed token tracking
   - Enhanced AI review prompt for more relevant feedback
   - Better error handling and improved UI experience
   - Comprehensive HTML user guide with screenshots
   - Recent repositories dropdown for quick access
   - Real-time review metrics (time taken and cost estimation)
   - Professional blue theme with dark/light mode support

3. **V2.0.0**
   - Modern UI with customtkinter components
   - Enhanced background image and visual aesthetics
   - Improved activity log with timestamped entries and scrollable text widget
   - Progress bar with percentage display for better user feedback
   - "Clear" button that resets both activity log and review metrics
   - Fixed Claude 4 Sonnet cost calculation with detailed token tracking
   - Enhanced AI review prompt for more relevant feedback
   - Better error handling and improved UI experience
   - Comprehensive HTML user guide with screenshots
   - Recent repositories dropdown for quick access
   - Real-time review metrics (time taken and cost estimation)
   - Professional blue theme with dark/light mode support

4. **v1.0.1**
   - Original stable version with basic UI
   - Core functionality for GitHub PR review
   - Token encryption for security

## How to Use

1. **Run Version Selector**
   ```powershell
   .\run_ai_review_selector.ps1
   ```

2. **Run Specific Version**
   - Latest Version: `.\dist\AIReviewTool_V2.1.3.exe` or `.\run_ai_review.ps1`
   - Previous Version: `.\dist\AIReviewTool_V2.1.2.exe`
   - v1.0.1: `.\dist\AIReviewTool_v1.0.1.exe` or `.\run_v1.0.1.ps1`

3. **Build Specific Version**
   - Latest Version: `.\build_v2.1.3.ps1`
   - Previous Version: `.\build_v2.1.2.ps1`
   - v1.0.1: `.\build_v1.0.1_simple.ps1`
