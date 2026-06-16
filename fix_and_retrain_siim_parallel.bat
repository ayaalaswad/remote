@echo off
REM ============================================================================
REM Complete SIIM Fix and Retrain Pipeline (PARALLEL)
REM Steps: 1) Diagnose 2) Fix splits 3) Launch 3 training windows in parallel
REM ============================================================================

echo ========================================
echo   SIIM Complete Fix and Retrain
echo   (PARALLEL MODE)
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
echo Press any key to launch 3 parallel training windows...
pause >nul

REM ============================================================================
REM STEP 3: LAUNCH PARALLEL TRAINING WINDOWS
REM ============================================================================

echo.
echo ========================================
echo   STEP 3: Launching Parallel Training
echo ========================================
echo.

cd BenchX

REM Launch each training in a new CMD window
echo Launching SIIM 1%%...
start "SIIM 1%%" cmd /k "python bin/train.py ../sharp_siim_1pct.yml"

timeout /t 2 >nul

echo Launching SIIM 10%%...
start "SIIM 10%%" cmd /k "python bin/train.py ../sharp_siim_10pct.yml"

timeout /t 2 >nul

echo Launching SIIM 100%%...
start "SIIM 100%%" cmd /k "python bin/train.py ../sharp_siim_100pct.yml"

cd ..

echo.
echo ========================================
echo   3 Training Windows Launched!
echo ========================================
echo.
echo Check the 3 new command windows:
echo   - "SIIM 1%%" window
echo   - "SIIM 10%%" window
echo   - "SIIM 100%%" window
echo.
echo Watch for:
echo   - Loss: 0.4-0.6 (NOT 0.00)
echo   - AUROC: 0.55-0.70 (NOT NaN)
echo   - Accuracy: 75-85%% (NOT 100%%)
echo.
echo After all complete:
echo   1. python calculate_f1_from_pushed_results.py
echo   2. push_siim_results.bat
echo.

pause
