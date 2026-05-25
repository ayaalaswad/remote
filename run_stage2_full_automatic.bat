@echo off
REM =============================================================================
REM MASTER SCRIPT: Preprocessing + Stage 2 Training (Fully Automatic)
REM =============================================================================
REM This script will:
REM   1. Run Stage 2 preprocessing (create CSVs) - ~15-30 min
REM   2. Automatically start Stage 2 training when preprocessing completes - ~4h
REM
REM Total time: ~4.5-5 hours
REM You can close remote desktop and come back later!
REM =============================================================================

echo.
echo =============================================================================
echo AUTOMATIC STAGE 2 PIPELINE - PREPROCESSING + TRAINING
echo =============================================================================
echo.
echo This will run EVERYTHING automatically:
echo   [1] Preprocessing: Create missing CSV files (~15-30 min)
echo   [2] Training: Fine-tune Exp #1 and Exp #3 (~4 hours)
echo.
echo Total time: ~4.5-5 hours
echo.
echo You can safely close this remote desktop window after starting!
echo Results will be saved to logs.
echo.
echo REQUIREMENTS:
echo   - MIMIC-CXR reports at D:\datasets\mimic-cxr-reports\reports\files\
echo   - Exp #1 checkpoint at D:\experiments\exp1_baseline\p3_best.pt
echo   - Exp #3 checkpoint at D:\experiments\exp3_full_sharp\p3_best.pt
echo.

REM Check if checkpoints exist
if not exist "D:\experiments\exp1_baseline\p3_best.pt" (
    echo ERROR: Exp #1 checkpoint not found!
    echo Expected: D:\experiments\exp1_baseline\p3_best.pt
    pause
    exit /b 1
)

if not exist "D:\experiments\exp3_full_sharp\p3_best.pt" (
    echo ERROR: Exp #3 checkpoint not found!
    echo Expected: D:\experiments\exp3_full_sharp\p3_best.pt
    pause
    exit /b 1
)

echo ✓ All checkpoints found
echo.
pause

REM Create logs directory
mkdir logs 2>nul

REM Start timestamp
echo [%DATE% %TIME%] Starting automatic pipeline > logs\stage2_master.log

echo.
echo =============================================================================
echo PHASE 1: PREPROCESSING (Create CSV files)
echo =============================================================================
echo [%DATE% %TIME%] Starting preprocessing...
echo.

REM Run preprocessing
python create_stage2_csvs.py

REM Check if preprocessing succeeded
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo =============================================================================
    echo ERROR: Preprocessing failed!
    echo =============================================================================
    echo.
    echo Please check the error messages above.
    echo [%DATE% %TIME%] FAILED: Preprocessing error >> logs\stage2_master.log
    pause
    exit /b 1
)

REM Verify output files exist
if not exist "D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned\mimic_cxr_sectioned.csv" (
    echo ERROR: mimic_cxr_sectioned.csv was not created!
    echo [%DATE% %TIME%] FAILED: Missing mimic_cxr_sectioned.csv >> logs\stage2_master.log
    pause
    exit /b 1
)

if not exist "D:\datasets\mimic_cxr_merged\splits_reports_metadata.csv" (
    echo ERROR: splits_reports_metadata.csv was not created!
    echo [%DATE% %TIME%] FAILED: Missing splits_reports_metadata.csv >> logs\stage2_master.log
    pause
    exit /b 1
)

echo.
echo =============================================================================
echo ✓ PREPROCESSING COMPLETE
echo =============================================================================
echo [%DATE% %TIME%] Preprocessing completed successfully >> logs\stage2_master.log
echo.
echo Created files:
echo   - D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned\mimic_cxr_sectioned.csv
echo   - D:\datasets\mimic_cxr_merged\splits_reports_metadata.csv
echo.

REM Short pause before training
timeout /t 5 /nobreak

echo.
echo =============================================================================
echo PHASE 2: STAGE 2 TRAINING (Exp #1 and Exp #3)
echo =============================================================================
echo [%DATE% %TIME%] Starting Stage 2 training...
echo.
echo [%DATE% %TIME%] Starting Stage 2 training >> logs\stage2_master.log

REM Run Stage 2 training
cd stage2_training
call run_exp1_exp3.bat

REM Check if training succeeded
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo =============================================================================
    echo WARNING: Stage 2 training had errors
    echo =============================================================================
    echo.
    echo Please check logs\exp1_train.log and logs\exp3_train.log
    echo [%DATE% %TIME%] FAILED: Training errors >> ..\logs\stage2_master.log
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo =============================================================================
echo ✓ ALL COMPLETE!
echo =============================================================================
echo [%DATE% %TIME%] All tasks completed successfully >> logs\stage2_master.log
echo.
echo Completed:
echo   ✓ Preprocessing (CSV creation)
echo   ✓ Stage 2 Training (Exp #1 and Exp #3)
echo.
echo Next steps:
echo   1. Check training logs: stage2_training\logs\exp1_train.log
echo   2. Check training logs: stage2_training\logs\exp3_train.log
echo   3. Run testing: cd stage2_training && run_test_exp1_exp3.bat
echo.
echo =============================================================================
echo.

pause
