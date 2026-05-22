@echo off
REM Stage 2: Fine-tune CXRMate with all 4 Stage 1 checkpoints
REM Run this after Stage 1 training completes
REM Total time: ~8 hours (2 hours per experiment)

echo ========================================
echo Stage 2 Fine-Tuning - All Experiments
echo ========================================
echo.
echo This will fine-tune CXRMate with 4 different Stage 1 checkpoints:
echo   - exp1: Baseline (bi, batch=32)
echo   - exp2: Paired Sampling (100%% co-pos)
echo   - exp3: Full SHARP (hard neg 60%%)
echo   - exp4: Large Batch (batch=512)
echo.
echo Total estimated time: 8 hours
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

REM Experiment 2: Paired Sampling
echo.
echo ========================================
echo [%TIME%] Starting Experiment 2: Paired Sampling
echo ========================================
python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp2_paired.yaml ^
    --stages_module tools.stages ^
    --train ^
    > ..\stage2_training\logs\exp2_train.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Experiment 2 training completed successfully
) else (
    echo [%TIME%] ERROR: Experiment 2 training failed - check logs\exp2_train.log
    pause
    exit /b 1
)

REM Experiment 3: Full SHARP
echo.
echo ========================================
echo [%TIME%] Starting Experiment 3: Full SHARP
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

REM Experiment 4: Large Batch
echo.
echo ========================================
echo [%TIME%] Starting Experiment 4: Large Batch
echo ========================================
python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp4_large.yaml ^
    --stages_module tools.stages ^
    --train ^
    > ..\stage2_training\logs\exp4_train.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Experiment 4 training completed successfully
) else (
    echo [%TIME%] ERROR: Experiment 4 training failed - check logs\exp4_train.log
    pause
    exit /b 1
)

echo.
echo ========================================
echo ALL TRAINING COMPLETE!
echo ========================================
echo.
echo Next step: Run run_all_tests.bat to evaluate all experiments
echo.
pause
