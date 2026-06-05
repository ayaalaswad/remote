@echo off
REM ============================================================================
REM BenchX Data Preprocessing - SIIM and RSNA
REM ============================================================================

echo ========================================
echo   BenchX Data Preprocessing
echo   This will take 20-30 minutes
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote

REM ============================================================================
REM Step 1: SIIM Preprocessing
REM ============================================================================
echo [1/2] Preprocessing SIIM dataset...
echo   Converting DICOM to PNG (512x512)
echo   Creating train/val/test splits
echo.

python preprocess_siim_adapted.py

if errorlevel 1 (
    echo [ERROR] SIIM preprocessing failed!
    pause
    exit /b 1
)

echo [OK] SIIM preprocessing complete
echo.

REM ============================================================================
REM Step 2: RSNA Preprocessing
REM ============================================================================
echo [2/2] Preprocessing RSNA dataset...
echo   Converting ~30k DICOM to PNG (512x512)
echo   This will take 10-15 minutes
echo.

python preprocess_rsna_adapted.py

if errorlevel 1 (
    echo [ERROR] RSNA preprocessing failed!
    pause
    exit /b 1
)

echo [OK] RSNA preprocessing complete
echo.

REM ============================================================================
REM Verify Results
REM ============================================================================
echo ========================================
echo   Verifying Preprocessed Data
echo ========================================
echo.

cd BenchX\datasets

dir SIIM\images | find "File(s)"
dir SIIM\*.txt
echo.

dir RSNA\images | find "File(s)"
dir RSNA\*.txt
echo.

echo ========================================
echo   Preprocessing Complete!
echo ========================================
echo.
echo Now you can run SIIM training:
echo   cd C:\Users\aya.alaswad\remote\BenchX
echo   python bin/train.py configs/classification/SIIM/sharp.yml
echo.
pause
