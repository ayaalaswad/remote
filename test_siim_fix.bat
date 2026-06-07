@echo off
REM ============================================================================
REM Test SIIM Preprocessing Fix
REM ============================================================================

echo ========================================
echo   Test SIIM Preprocessing Fix
echo ========================================
echo.
echo This will:
echo   1. Delete old SIIM preprocessing
echo   2. Run fixed preprocessing script
echo   3. Verify validation has both classes
echo.
pause

cd C:\Users\aya.alaswad\remote

REM Pull latest code
echo Pulling latest code...
git pull origin main
echo.

REM Delete old preprocessing if it exists
if exist "BenchX\datasets\SIIM" (
    echo Deleting old SIIM preprocessing...
    rmdir /S /Q "BenchX\datasets\SIIM"
    echo Done
    echo.
)

REM Run fixed preprocessing
echo Running fixed preprocessing script...
python preprocess_siim_fixed.py

if errorlevel 1 (
    echo.
    echo [ERROR] Preprocessing failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Preprocessing Complete!
echo ========================================
echo.
echo Check the output above for:
echo   - Positive (pneumothorax) count
echo   - Negative (no pneumothorax) count
echo   - Validation split should have BOTH classes
echo.
echo If validation shows both classes, the fix worked!
echo.

pause
