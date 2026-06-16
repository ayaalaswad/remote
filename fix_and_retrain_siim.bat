@echo off
REM ============================================================================
REM Complete SIIM Fix and Retrain Pipeline
REM Steps: 1) Diagnose 2) Fix splits 3) Retrain all 3 experiments
REM ============================================================================

echo ========================================
echo   SIIM Complete Fix and Retrain
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote

REM ============================================================================
REM STEP 1 & 2: DIAGNOSE AND FIX SPLITS
REM ============================================================================

echo.
echo ========================================
echo   STEP 1 ^& 2: Diagnose ^& Fix Splits
echo ========================================
echo.

python fix_siim_complete.py

if errorlevel 1 (
    echo.
    echo [ERROR] Fix failed!
    pause
    exit /b 1
)

echo.
echo [OK] Splits fixed successfully!
echo.
echo Press any key to start retraining (will take 3-6 hours), or Ctrl+C to cancel...
pause >nul

REM ============================================================================
REM STEP 3: RETRAIN ALL 3 SIIM EXPERIMENTS
REM ============================================================================

echo.
echo ========================================
echo   STEP 3: Retraining SIIM Experiments
echo ========================================
echo.

cd BenchX

REM ---------- SIIM 1% ----------
echo.
echo [1/3] Training SIIM 1%%...
echo Started at %time%
echo.

python bin/train.py ../sharp_siim_1pct.yml

if errorlevel 1 (
    echo.
    echo [WARNING] SIIM 1%% training failed or interrupted!
    echo.
) else (
    echo.
    echo [OK] SIIM 1%% completed at %time%
    echo.
)

REM ---------- SIIM 10% ----------
echo.
echo [2/3] Training SIIM 10%%...
echo Started at %time%
echo.

python bin/train.py ../sharp_siim_10pct.yml

if errorlevel 1 (
    echo.
    echo [WARNING] SIIM 10%% training failed or interrupted!
    echo.
) else (
    echo.
    echo [OK] SIIM 10%% completed at %time%
    echo.
)

REM ---------- SIIM 100% ----------
echo.
echo [3/3] Training SIIM 100%%...
echo Started at %time%
echo.

python bin/train.py ../sharp_siim_100pct.yml

if errorlevel 1 (
    echo.
    echo [WARNING] SIIM 100%% training failed or interrupted!
    echo.
) else (
    echo.
    echo [OK] SIIM 100%% completed at %time%
    echo.
)

cd ..

REM ============================================================================
REM COMPLETE
REM ============================================================================

echo.
echo ========================================
echo   ALL TRAINING COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Run: python calculate_f1_from_pushed_results.py
echo 2. Check F1 scores are reasonable (not 0%%)
echo 3. Push results: push_siim_results.bat
echo.

pause
