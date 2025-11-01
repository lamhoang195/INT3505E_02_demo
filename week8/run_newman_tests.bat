@echo off
REM ========================================
REM Newman Test Runner for Windows
REM ========================================

echo.
echo ========================================
echo  Newman API Tests - Library Management
echo ========================================
echo.

REM Change to week8 directory
cd /d "%~dp0"

REM Check if Newman is installed
where newman >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Newman is not installed!
    echo Please install Newman first: npm install -g newman
    echo.
    pause
    exit /b 1
)

REM Run Newman tests
echo [INFO] Running tests with Newman...
echo.
newman run Library_API_Tests.postman_collection.json ^
  --reporters cli,html ^
  --reporter-html-export newman-report.html ^
  --delay-request 50

echo.
echo ========================================
echo  Test Results
echo ========================================
echo.

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] All tests passed! ✓
    echo.
    echo HTML Report: newman-report.html
    echo.
    
    REM Ask to open HTML report
    set /p OPEN_REPORT="Open HTML report? (y/n): "
    if /i "%OPEN_REPORT%"=="y" (
        start newman-report.html
    )
) else (
    echo [FAILED] Some tests failed! ✗
    echo Check the output above for details.
)

echo.
pause
