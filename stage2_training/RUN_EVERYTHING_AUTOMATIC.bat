@echo off
REM =============================================================================
REM MASTER SCRIPT: Runs EVERYTHING automatically
REM =============================================================================
REM This script will:
REM   1. Train all 4 experiments in parallel (~2 hours)
REM   2. Wait for training to complete
REM   3. Test all 4 experiments in parallel (~30 min)
REM   4. Wait for testing to complete
REM   5. Extract and summarize results (~1 min)
REM
REM Total time: ~2.5 hours
REM You can close remote desktop and come back later!
REM =============================================================================

echo.
echo =============================================================================
echo AUTOMATIC STAGE 2 PIPELINE - COMPLETE RUN
echo =============================================================================
echo.
echo This will run EVERYTHING automatically:
echo   [1] Training (4 experiments in parallel, ~2 hours)
echo   [2] Testing (4 experiments in parallel, ~30 min)
echo   [3] Results extraction (automatic)
echo.
echo Total time: ~2.5 hours
echo.
echo You can safely close this remote desktop window after starting!
echo Results will be saved to logs and results files.
echo.
echo REQUIREMENTS:
echo   - Exp4 Stage 1 must be FINISHED
echo   - CheXbert checkpoint downloaded
echo   - All dependencies installed
echo.

REM Check if exp4 checkpoint exists
if not exist "D:\experiments\exp4_large_batch\p3_best.pt" (
    echo ERROR: Exp4 Stage 1 checkpoint not found!
    echo Please wait for exp4 to finish training first.
    echo Check: dir D:\experiments\exp4_large_batch\p3_best.pt
    pause
    exit /b 1
)

echo Exp4 checkpoint found: OK
echo.
pause

REM Create logs directory
mkdir logs 2>nul

REM Start timestamp
echo [%DATE% %TIME%] Starting automatic pipeline > logs\master_log.txt

echo.
echo =============================================================================
echo PHASE 1: TRAINING (4 experiments in parallel)
echo =============================================================================
echo [%DATE% %TIME%] Starting training phase...
echo.

cd C:\Users\aya.alaswad\remote\cxrmate

REM Launch all 4 training jobs
start "EXP1-Train" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp1_baseline.yaml --stages_module tools.stages --train > ..\stage2_training\logs\exp1_train.log 2>&1 && echo TRAINING_COMPLETE > ..\stage2_training\logs\exp1_train.done"
echo [%TIME%] Launched Experiment 1 training

timeout /t 5 /nobreak >nul

start "EXP2-Train" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp2_paired.yaml --stages_module tools.stages --train > ..\stage2_training\logs\exp2_train.log 2>&1 && echo TRAINING_COMPLETE > ..\stage2_training\logs\exp2_train.done"
echo [%TIME%] Launched Experiment 2 training

timeout /t 5 /nobreak >nul

start "EXP3-Train" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp3_full.yaml --stages_module tools.stages --train > ..\stage2_training\logs\exp3_train.log 2>&1 && echo TRAINING_COMPLETE > ..\stage2_training\logs\exp3_train.done"
echo [%TIME%] Launched Experiment 3 training

timeout /t 5 /nobreak >nul

start "EXP4-Train" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp4_large.yaml --stages_module tools.stages --train > ..\stage2_training\logs\exp4_train.log 2>&1 && echo TRAINING_COMPLETE > ..\stage2_training\logs\exp4_train.done"
echo [%TIME%] Launched Experiment 4 training

echo.
echo All 4 training jobs launched!
echo Now waiting for all to complete...
echo This will take approximately 2 hours.
echo.
echo [%DATE% %TIME%] All training jobs launched >> logs\master_log.txt

REM Wait for all training to complete
:WAIT_TRAINING
timeout /t 60 /nobreak >nul

REM Check if all done files exist
set DONE_COUNT=0
if exist "logs\exp1_train.done" set /a DONE_COUNT+=1
if exist "logs\exp2_train.done" set /a DONE_COUNT+=1
if exist "logs\exp3_train.done" set /a DONE_COUNT+=1
if exist "logs\exp4_train.done" set /a DONE_COUNT+=1

echo [%TIME%] Training progress: %DONE_COUNT%/4 experiments completed
echo [%DATE% %TIME%] Training progress: %DONE_COUNT%/4 completed >> logs\master_log.txt

if %DONE_COUNT% LSS 4 goto WAIT_TRAINING

echo.
echo =============================================================================
echo TRAINING COMPLETE! All 4 experiments finished.
echo =============================================================================
echo [%DATE% %TIME%] Training phase complete >> logs\master_log.txt
echo.

REM Small delay before testing
timeout /t 10 /nobreak >nul

echo.
echo =============================================================================
echo PHASE 2: TESTING (4 experiments in parallel)
echo =============================================================================
echo [%DATE% %TIME%] Starting testing phase...
echo.

REM Launch all 4 testing jobs
start "EXP1-Test" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp1_baseline.yaml --stages_module tools.stages --test > ..\stage2_training\logs\exp1_test.log 2>&1 && echo TESTING_COMPLETE > ..\stage2_training\logs\exp1_test.done"
echo [%TIME%] Launched Experiment 1 testing

timeout /t 5 /nobreak >nul

start "EXP2-Test" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp2_paired.yaml --stages_module tools.stages --test > ..\stage2_training\logs\exp2_test.log 2>&1 && echo TESTING_COMPLETE > ..\stage2_training\logs\exp2_test.done"
echo [%TIME%] Launched Experiment 2 testing

timeout /t 5 /nobreak >nul

start "EXP3-Test" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp3_full.yaml --stages_module tools.stages --test > ..\stage2_training\logs\exp3_test.log 2>&1 && echo TESTING_COMPLETE > ..\stage2_training\logs\exp3_test.done"
echo [%TIME%] Launched Experiment 3 testing

timeout /t 5 /nobreak >nul

start "EXP4-Test" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp4_large.yaml --stages_module tools.stages --test > ..\stage2_training\logs\exp4_test.log 2>&1 && echo TESTING_COMPLETE > ..\stage2_training\logs\exp4_test.done"
echo [%TIME%] Launched Experiment 4 testing

echo.
echo All 4 testing jobs launched!
echo Now waiting for all to complete...
echo This will take approximately 30 minutes.
echo.
echo [%DATE% %TIME%] All testing jobs launched >> logs\master_log.txt

REM Wait for all testing to complete
:WAIT_TESTING
timeout /t 60 /nobreak >nul

REM Check if all done files exist
set DONE_COUNT=0
if exist "logs\exp1_test.done" set /a DONE_COUNT+=1
if exist "logs\exp2_test.done" set /a DONE_COUNT+=1
if exist "logs\exp3_test.done" set /a DONE_COUNT+=1
if exist "logs\exp4_test.done" set /a DONE_COUNT+=1

echo [%TIME%] Testing progress: %DONE_COUNT%/4 experiments completed
echo [%DATE% %TIME%] Testing progress: %DONE_COUNT%/4 completed >> logs\master_log.txt

if %DONE_COUNT% LSS 4 goto WAIT_TESTING

echo.
echo =============================================================================
echo TESTING COMPLETE! All 4 experiments finished.
echo =============================================================================
echo [%DATE% %TIME%] Testing phase complete >> logs\master_log.txt
echo.

REM Small delay before results extraction
timeout /t 5 /nobreak >nul

echo.
echo =============================================================================
echo PHASE 3: RESULTS EXTRACTION
echo =============================================================================
echo [%DATE% %TIME%] Extracting results...
echo.

cd ..\stage2_training

REM Extract all metrics
python extract_results.py > logs\extract_results.txt 2>&1
echo [%TIME%] Extracted all metrics

REM Extract per-condition analysis
python per_condition_analysis.py > logs\per_condition_analysis.txt 2>&1
echo [%TIME%] Extracted per-condition F1 scores

echo.
echo [%DATE% %TIME%] Results extraction complete >> logs\master_log.txt

echo.
echo =============================================================================
echo ALL DONE! PIPELINE COMPLETE
echo =============================================================================
echo.
echo Results saved to:
echo   - logs\exp1_train.log, logs\exp1_test.log
echo   - logs\exp2_train.log, logs\exp2_test.log
echo   - logs\exp3_train.log, logs\exp3_test.log
echo   - logs\exp4_train.log, logs\exp4_test.log
echo   - results_all_metrics.json
echo   - results_per_condition.csv
echo   - logs\extract_results.txt (summary)
echo   - logs\per_condition_analysis.txt (per-condition summary)
echo.

REM Display quick summary
echo =============================================================================
echo QUICK SUMMARY (see full results in files above)
echo =============================================================================
type logs\extract_results.txt | findstr "CheXbert F1"
echo.

REM Final timestamp
echo [%DATE% %TIME%] Pipeline complete! >> logs\master_log.txt

echo.
echo Check logs\master_log.txt for full timeline.
echo.
echo You can now use these results for your paper rebuttal!
echo.
pause
