# ========================================
# Newman Test Runner for PowerShell
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Newman API Tests - Library Management" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check if Newman is installed
$newmanInstalled = Get-Command newman -ErrorAction SilentlyContinue
if (-not $newmanInstalled) {
    Write-Host "[ERROR] Newman is not installed!" -ForegroundColor Red
    Write-Host "Please install Newman first: npm install -g newman" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Run Newman tests
Write-Host "[INFO] Running tests with Newman..." -ForegroundColor Yellow
Write-Host ""

$exitCode = 0
try {
    newman run Library_API_Tests.postman_collection.json `
      --reporters cli,html `
      --reporter-html-export newman-report.html `
      --delay-request 50
    
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host "[ERROR] Failed to run Newman: $_" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Test Results" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($exitCode -eq 0) {
    Write-Host "[SUCCESS] All tests passed! ✓" -ForegroundColor Green
    Write-Host ""
    Write-Host "HTML Report: newman-report.html" -ForegroundColor Cyan
    Write-Host ""
    
    # Ask to open HTML report
    $openReport = Read-Host "Open HTML report? (y/n)"
    if ($openReport -eq "y" -or $openReport -eq "Y") {
        Start-Process newman-report.html
    }
} else {
    Write-Host "[FAILED] Some tests failed! ✗" -ForegroundColor Red
    Write-Host "Check the output above for details." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
