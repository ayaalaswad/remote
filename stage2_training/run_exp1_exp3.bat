@echo off
REM Stage 2: Fine-tune CXRMate with Exp #1 and Exp #3 only
REM
REM Skip Exp #2 (collapsed) and Exp #4 (waiting for v2)
REM Total time: ~4 hours (2 hours per experiment)

echo ========================================
echo Stage 2 Fine-Tuning - Exp 1 and Exp 3
echo ========================================
echo.
echo This will fine-tune CXRMate with 2 Stage 1 checkpoints:
echo   - Exp #1: Baseline (6.61%% R@1)
echo   - Exp #3: Hard Negatives (6.21%% R@1)
echo.
echo Skipping:
echo   - Exp #2: Paired sampling (collapsed to 0.81%%)
echo   - Exp #4: Waiting for v2 (proper 100k steps training)
echo.
echo Total estimated time: 4 hours
echo.
pause

cd C:\Users\aya.alaswad\remote\cxrmate

REM Experiment 1: Baseline
echo.
echo ========================================
echo [%TIME%] Starting Experiment 1: Baseline
echo ========================================
python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp1_baseline.yaml ^
    --stages_module tools.stages ^
    --train ^
    > ..\stage2_training\logs\exp1_train.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Experiment 1 training completed successfully
) else (
    echo [%TIME%] ERROR: Experiment 1 training failed - check logs\exp1_train.log
    pause
    exit /b 1
)

REM Experiment 3: Hard Negatives
echo.
echo ========================================
echo [%TIME%] Starting Experiment 3: Hard Negatives
echo ========================================
python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp3_full.yaml ^
    --stages_module tools.stages ^
    --train ^
    > ..\stage2_training\logs\exp3_train.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Experiment 3 training completed successfully
) else (
    echo [%TIME%] ERROR: Experiment 3 training failed - check logs\exp3_train.log
    pause
    exit /b 1
)

echo.
echo ========================================
echo Training Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Run testing: run_test_exp1_exp3.bat
echo   2. Extract results: python extract_results.py
echo.
pause
