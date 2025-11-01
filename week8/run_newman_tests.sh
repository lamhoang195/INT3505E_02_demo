#!/bin/bash

# ========================================
# Newman Test Runner for Linux/Mac
# ========================================

echo ""
echo "========================================"
echo " Newman API Tests - Library Management"
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Check if Newman is installed
if ! command -v newman &> /dev/null; then
    echo "[ERROR] Newman is not installed!"
    echo "Please install Newman first: npm install -g newman"
    echo ""
    exit 1
fi

# Run Newman tests
echo "[INFO] Running tests with Newman..."
echo ""

newman run Library_API_Tests.postman_collection.json \
  --reporters cli,html \
  --reporter-html-export newman-report.html \
  --delay-request 50

EXIT_CODE=$?

echo ""
echo "========================================"
echo " Test Results"
echo "========================================"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "[SUCCESS] All tests passed! ✓"
    echo ""
    echo "HTML Report: newman-report.html"
    echo ""
    
    # Ask to open HTML report (for systems with xdg-open or open)
    read -p "Open HTML report? (y/n): " OPEN_REPORT
    if [ "$OPEN_REPORT" = "y" ] || [ "$OPEN_REPORT" = "Y" ]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open newman-report.html
        elif command -v open &> /dev/null; then
            open newman-report.html
        else
            echo "Could not open report automatically. Please open newman-report.html manually."
        fi
    fi
else
    echo "[FAILED] Some tests failed! ✗"
    echo "Check the output above for details."
fi

echo ""
