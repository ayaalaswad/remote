@echo off
REM Stage 2: Test CXRMate with Exp #1 and Exp #3
REM Run this after training completes
REM Total time: ~1 hour (30 min per experiment)

echo ========================================
echo Stage 2 Testing - Exp 1 and Exp 3
echo ========================================
echo.
pause

cd C:\Users\aya.alaswad\remote\cxrmate

REM Test Experiment 1: Baseline
echo.
echo ========================================
echo [%TIME%] Testing Experiment 1: Baseline
echo ========================================
python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp1_baseline.yaml ^
    --stages_module tools.stages ^
    --test ^
    > ..\stage2_training\logs\exp1_test.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Experiment 1 testing completed successfully
) else (
    echo [%TIME%] ERROR: Experiment 1 testing failed - check logs\exp1_test.log
    pause
    exit /b 1
)

REM Test Experiment 3: Hard Negatives
echo.
echo ========================================
echo [%TIME%] Testing Experiment 3: Hard Negatives
echo ========================================
python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp3_full.yaml ^
    --stages_module tools.stages ^
    --test ^
    > ..\stage2_training\logs\exp3_test.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Experiment 3 testing completed successfully
) else (
    echo [%TIME%] ERROR: Experiment 3 testing failed - check logs\exp3_test.log
    pause
    exit /b 1
)

echo.
echo ========================================
echo Testing Complete!
echo ========================================
echo.
echo Next step: Extract results
echo   python extract_results.py
echo.
pause
