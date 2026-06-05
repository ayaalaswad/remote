@echo off
REM ============================================================================
REM Run BenchX preprocessing for SIIM and RSNA
REM ============================================================================

echo ========================================
echo   BenchX Data Preprocessing
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote\BenchX

REM ============================================================================
REM RSNA Preprocessing (has proper script)
REM ============================================================================
echo [1/2] Preprocessing RSNA dataset...
echo   This will take 10-15 minutes (converting ~30k DICOM images to PNG)
echo.

python preprocess\datasets\RSNA\preprocess_rsna.py

if errorlevel 1 (
    echo [ERROR] RSNA preprocessing failed!
    pause
    exit /b 1
)

echo [OK] RSNA preprocessing complete
echo.

REM ============================================================================
REM SIIM Preprocessing (needs custom adaptation)
REM ============================================================================
echo [2/2] SIIM requires manual adaptation...
echo   BenchX's script expects stage_1 PNG files, but we have stage_2 DICOM
echo   Skipping for now - will use simpler approach
echo.

echo ========================================
echo   Preprocessing Complete!
echo ========================================
echo.
pause
