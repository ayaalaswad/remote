@echo off
REM =============================================================================
REM RadDINO Stage 2: Fine-tune CXRMate with RadDINO checkpoint
REM =============================================================================
REM This script will:
REM   1. Fine-tune CXRMate with RadDINO encoder (10 epochs) - ~2 hours
REM   2. Test on MIMIC-CXR test set - ~15 min
REM   3. Extract CheXbert F1 results - ~1 min
REM
REM Total time: ~2 hours 15 min
REM You can close remote desktop and come back later!
REM =============================================================================

echo.
echo =============================================================================
echo RadDINO STAGE 2 FINE-TUNING
echo =============================================================================
echo.
echo This will fine-tune CXRMate with RadDINO Stage 1 checkpoint:
echo   - Checkpoint: D:\experiments\exp_raddino_hardneg\p3_best.pt
echo   - Stage 1 R@1: 10.26%%
echo.
echo Total estimated time: ~2 hours
echo.

REM Check if checkpoint exists
if not exist "D:\experiments\exp_raddino_hardneg\p3_best.pt" (
    echo ERROR: RadDINO checkpoint not found!
    echo Expected: D:\experiments\exp_raddino_hardneg\p3_best.pt
    echo.
    echo Please verify:
    echo   1. RadDINO Stage 1 training completed
    echo   2. Checkpoint was saved correctly
    pause
    exit /b 1
)

echo [OK] RadDINO checkpoint found
echo.

REM Check if CXRMate directory exists
if not exist "C:\Users\aya.alaswad\remote\cxrmate" (
    echo ERROR: CXRMate directory not found!
    echo Expected: C:\Users\aya.alaswad\remote\cxrmate
    echo.
    echo Please verify CXRMate is properly set up.
    pause
    exit /b 1
)

echo [OK] CXRMate directory found
echo.

REM Check if preprocessing is done
if not exist "D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned\mimic_cxr_sectioned.csv" (
    echo ERROR: Stage 2 preprocessing not done!
    echo.
    echo Please run preprocessing first:
    echo   cd stage2_training
    echo   run_preprocessing.bat
    pause
    exit /b 1
)

echo [OK] Preprocessing complete
echo.

pause

REM Create logs directory
mkdir stage2_training\logs 2>nul

echo.
echo =============================================================================
echo PHASE 1: TRAINING (10 epochs, ~2 hours)
echo =============================================================================
echo [%TIME%] Starting RadDINO Stage 2 training...
echo.

cd C:\Users\aya.alaswad\remote\cxrmate

python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp_raddino.yaml ^
    --stages_module tools.stages ^
    --train ^
    > ..\stage2_training\logs\raddino_train.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [%TIME%] Training completed successfully!
) else (
    echo.
    echo ERROR: Training failed - check stage2_training\logs\raddino_train.log
    cd C:\Users\aya.alaswad\remote\MyReasearch
    pause
    exit /b 1
)

echo.
echo =============================================================================
echo PHASE 2: TESTING (~15 min)
echo =============================================================================
echo [%TIME%] Starting RadDINO Stage 2 testing...
echo.

python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp_raddino.yaml ^
    --stages_module tools.stages ^
    --test ^
    > ..\stage2_training\logs\raddino_test.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [%TIME%] Testing completed successfully!
) else (
    echo.
    echo ERROR: Testing failed - check stage2_training\logs\raddino_test.log
    cd C:\Users\aya.alaswad\remote\MyReasearch
    pause
    exit /b 1
)

cd C:\Users\aya.alaswad\remote\MyReasearch

echo.
echo =============================================================================
echo [OK] ALL COMPLETE!
echo =============================================================================
echo.
echo Completed:
echo   [OK] Training (10 epochs)
echo   [OK] Testing on MIMIC-CXR test set
echo.
echo Logs saved to:
echo   - stage2_training\logs\raddino_train.log
echo   - stage2_training\logs\raddino_test.log
echo.
echo Next steps:
echo   1. Extract CheXbert F1: python extract_raddino_results.py
echo   2. Compare with main SHARP (Exp #3)
echo.
echo =============================================================================
echo.

pause
