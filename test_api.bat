@echo off
echo Testing AI Review API with Claude v4 Sonnet model
echo ==============================================

REM Get directory of this script
set SCRIPT_DIR=%~dp0
cd %SCRIPT_DIR%

REM Run the test script
python AIReview\test_api.py --text "Function test(a, b) { return a + b; }"

echo.
echo Test complete. If successful, you should see feedback from the AI above.
pause
