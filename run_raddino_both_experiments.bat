@echo off
REM =============================================================================
REM RadDINO Stage 2 - Both Experiments (Sequential)
REM =============================================================================
REM This script runs:
REM   Experiment 1: RadDINO + SHARP Stage 1 (hard negatives trained)
REM   Experiment 2: RadDINO vanilla (raw HuggingFace weights)
REM
REM Both use IDENTICAL Stage 2 settings for fair comparison.
REM
REM Total time: ~4.5 hours (2 hours per experiment + setup)
REM =============================================================================

echo.
echo =============================================================================
echo RadDINO Stage 2 - Both Experiments
echo =============================================================================
echo.
echo This will run TWO experiments sequentially:
echo.
echo   [Experiment 1] RadDINO + SHARP Stage 1
echo                  Checkpoint: D:\experiments\exp_raddino_hardneg\p3_best.pt
echo                  Stage 1 R@1: 10.26%%
echo                  Stage 2: 10 epochs (~2 hours)
echo.
echo   [Experiment 2] RadDINO vanilla baseline
echo                  Checkpoint: microsoft/rad-dino (raw pretrained)
echo                  Stage 1: None (no training)
echo                  Stage 2: 10 epochs (~2 hours)
echo.
echo Both experiments use IDENTICAL Stage 2 settings:
echo   - Learning rate: 5e-5
echo   - Epochs: 10
echo   - Batch size: 32 (effective)
echo   - Encoder: Unfrozen (fine-tuned end-to-end)
echo.
echo Total time: ~4.5 hours
echo.
echo You can close remote desktop after starting!
echo.
pause

REM Create logs directory
mkdir stage2_training\logs 2>nul

REM Start master log
echo [%DATE% %TIME%] Starting RadDINO experiments >> stage2_training\logs\raddino_master.log

REM =============================================================================
REM STEP 0: Verify Experiment 1 checkpoint exists
REM =============================================================================
echo.
echo =============================================================================
echo STEP 0: Verifying prerequisites
echo =============================================================================
echo.

if not exist "D:\experiments\exp_raddino_hardneg\p3_best.pt" (
    echo [ERROR] Experiment 1 checkpoint not found!
    echo         Expected: D:\experiments\exp_raddino_hardneg\p3_best.pt
    echo.
    echo Please verify RadDINO Stage 1 training completed successfully.
    echo [%DATE% %TIME%] FAILED: Missing Exp1 checkpoint >> stage2_training\logs\raddino_master.log
    pause
    exit /b 1
)

echo [OK] Experiment 1 checkpoint found
echo      D:\experiments\exp_raddino_hardneg\p3_best.pt
echo.

REM Check CXRMate
if not exist "C:\Users\aya.alaswad\remote\cxrmate" (
    echo [ERROR] CXRMate directory not found!
    echo         Expected: C:\Users\aya.alaswad\remote\cxrmate
    echo.
    echo [%DATE% %TIME%] FAILED: Missing CXRMate >> stage2_training\logs\raddino_master.log
    pause
    exit /b 1
)

echo [OK] CXRMate directory found
echo.

REM Check preprocessing
if not exist "D:\datasets\mimic-cxr-jpg\mimic_cxr_sectioned\mimic_cxr_sectioned.csv" (
    echo [ERROR] Stage 2 preprocessing not done!
    echo.
    echo Please run preprocessing first:
    echo   cd stage2_training
    echo   run_preprocessing.bat
    echo.
    echo [%DATE% %TIME%] FAILED: Missing preprocessing >> stage2_training\logs\raddino_master.log
    pause
    exit /b 1
)

echo [OK] Preprocessing complete
echo.

REM =============================================================================
REM STEP 1: Create vanilla RadDINO checkpoint (if needed)
REM =============================================================================
echo.
echo =============================================================================
echo STEP 1: Preparing Experiment 2 checkpoint
echo =============================================================================
echo.

if exist "D:\experiments\raddino_vanilla\pretrained.pt" (
    echo [OK] Vanilla RadDINO checkpoint already exists
    echo      D:\experiments\raddino_vanilla\pretrained.pt
    echo      Skipping creation
    echo.
) else (
    echo [INFO] Creating vanilla RadDINO checkpoint...
    echo        This extracts microsoft/rad-dino weights
    echo        Takes ~2-5 minutes
    echo.

    python create_raddino_vanilla_checkpoint.py

    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo [ERROR] Failed to create vanilla RadDINO checkpoint!
        echo         See error messages above
        echo.
        echo [%DATE% %TIME%] FAILED: Vanilla checkpoint creation >> stage2_training\logs\raddino_master.log
        pause
        exit /b 1
    )

    echo.
    echo [OK] Vanilla RadDINO checkpoint created
    echo.
)

echo [%DATE% %TIME%] Prerequisites verified >> stage2_training\logs\raddino_master.log

call write_progress.bat "RadDINO experiments started - Setup complete"

REM =============================================================================
REM EXPERIMENT 1: RadDINO + SHARP Stage 1
REM =============================================================================
echo.
echo =============================================================================
echo EXPERIMENT 1: RadDINO + SHARP Stage 1
echo =============================================================================
echo [%TIME%] Starting training (10 epochs, ~2 hours)...
echo.
echo Config: stage2_training\configs\exp_raddino.yaml
echo Checkpoint: D:\experiments\exp_raddino_hardneg\p3_best.pt
echo.

echo [%DATE% %TIME%] Starting Experiment 1 >> stage2_training\logs\raddino_master.log

call write_progress.bat "Experiment 1 (RadDINO+SHARP) - Training started (~2h)"

cd C:\Users\aya.alaswad\remote\cxrmate

REM Training
python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp_raddino.yaml ^
    --stages_module tools.stages ^
    --train ^
    > ..\stage2_training\logs\raddino_exp1_train.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [%TIME%] Training completed successfully!
    cd C:\Users\aya.alaswad\remote\MyReasearch
    call write_progress.bat "Experiment 1 - Training complete! Starting testing (~15min)"
    cd C:\Users\aya.alaswad\remote\cxrmate
) else (
    echo.
    echo [ERROR] Training failed - check stage2_training\logs\raddino_exp1_train.log
    echo [%DATE% %TIME%] FAILED: Experiment 1 training >> ..\stage2_training\logs\raddino_master.log
    cd C:\Users\aya.alaswad\remote\MyReasearch
    call write_progress.bat "ERROR: Experiment 1 training FAILED - check logs"
    pause
    exit /b 1
)

echo [%DATE% %TIME%] Experiment 1 training complete >> ..\stage2_training\logs\raddino_master.log

REM Testing
echo.
echo [%TIME%] Starting testing (~15 min)...
echo.

python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp_raddino.yaml ^
    --stages_module tools.stages ^
    --test ^
    > ..\stage2_training\logs\raddino_exp1_test.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [%TIME%] Testing completed successfully!
    cd C:\Users\aya.alaswad\remote\MyReasearch
    call write_progress.bat "Experiment 1 COMPLETE! Starting Experiment 2 (~2h 15m)"
    cd C:\Users\aya.alaswad\remote\cxrmate
) else (
    echo.
    echo [ERROR] Testing failed - check stage2_training\logs\raddino_exp1_test.log
    echo [%DATE% %TIME%] FAILED: Experiment 1 testing >> ..\stage2_training\logs\raddino_master.log
    cd C:\Users\aya.alaswad\remote\MyReasearch
    call write_progress.bat "ERROR: Experiment 1 testing FAILED - check logs"
    pause
    exit /b 1
)

cd C:\Users\aya.alaswad\remote\MyReasearch

echo [%DATE% %TIME%] Experiment 1 complete >> stage2_training\logs\raddino_master.log

echo.
echo [OK] Experiment 1 complete!
echo.

REM Short pause before next experiment
timeout /t 10 /nobreak

REM =============================================================================
REM EXPERIMENT 2: RadDINO Vanilla Baseline
REM =============================================================================
echo.
echo =============================================================================
echo EXPERIMENT 2: RadDINO Vanilla Baseline
echo =============================================================================
echo [%TIME%] Starting training (10 epochs, ~2 hours)...
echo.
echo Config: stage2_training\configs\exp_raddino_vanilla.yaml
echo Checkpoint: D:\experiments\raddino_vanilla\pretrained.pt
echo.

echo [%DATE% %TIME%] Starting Experiment 2 >> stage2_training\logs\raddino_master.log

cd C:\Users\aya.alaswad\remote\cxrmate

REM Training
python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp_raddino_vanilla.yaml ^
    --stages_module tools.stages ^
    --train ^
    > ..\stage2_training\logs\raddino_exp2_train.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [%TIME%] Training completed successfully!
    cd C:\Users\aya.alaswad\remote\MyReasearch
    call write_progress.bat "Experiment 2 - Training complete! Starting testing (~15min)"
    cd C:\Users\aya.alaswad\remote\cxrmate
) else (
    echo.
    echo [ERROR] Training failed - check stage2_training\logs\raddino_exp2_train.log
    echo [%DATE% %TIME%] FAILED: Experiment 2 training >> ..\stage2_training\logs\raddino_master.log
    cd C:\Users\aya.alaswad\remote\MyReasearch
    call write_progress.bat "ERROR: Experiment 2 training FAILED - check logs"
    pause
    exit /b 1
)

echo [%DATE% %TIME%] Experiment 2 training complete >> ..\stage2_training\logs\raddino_master.log

REM Testing
echo.
echo [%TIME%] Starting testing (~15 min)...
echo.

python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp_raddino_vanilla.yaml ^
    --stages_module tools.stages ^
    --test ^
    > ..\stage2_training\logs\raddino_exp2_test.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [%TIME%] Testing completed successfully!
    cd C:\Users\aya.alaswad\remote\MyReasearch
    call write_progress.bat "Experiment 2 COMPLETE! Generating comparison report..."
    cd C:\Users\aya.alaswad\remote\cxrmate
) else (
    echo.
    echo [ERROR] Testing failed - check stage2_training\logs\raddino_exp2_test.log
    echo [%DATE% %TIME%] FAILED: Experiment 2 testing >> ..\stage2_training\logs\raddino_master.log
    cd C:\Users\aya.alaswad\remote\MyReasearch
    call write_progress.bat "ERROR: Experiment 2 testing FAILED - check logs"
    pause
    exit /b 1
)

cd C:\Users\aya.alaswad\remote\MyReasearch

echo [%DATE% %TIME%] Experiment 2 complete >> stage2_training\logs\raddino_master.log

echo.
echo [OK] Experiment 2 complete!
echo.

REM =============================================================================
REM DONE - Extract results
REM =============================================================================
echo.
echo =============================================================================
echo [OK] ALL EXPERIMENTS COMPLETE!
echo =============================================================================
echo [%DATE% %TIME%] All experiments complete >> stage2_training\logs\raddino_master.log
echo.
echo Completed:
echo   [OK] Experiment 1: RadDINO + SHARP Stage 1
echo   [OK] Experiment 2: RadDINO vanilla baseline
echo.
echo Logs saved to:
echo   - stage2_training\logs\raddino_exp1_train.log
echo   - stage2_training\logs\raddino_exp1_test.log
echo   - stage2_training\logs\raddino_exp2_train.log
echo   - stage2_training\logs\raddino_exp2_test.log
echo   - stage2_training\logs\raddino_master.log
echo.
echo.
echo =============================================================================
echo EXTRACTING RESULTS AND GENERATING REPORT
echo =============================================================================
echo [%TIME%] Running comparison analysis...
echo.

python compare_raddino_experiments.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [%TIME%] Analysis complete!
    call write_progress.bat "ALL DONE! Results in raddino_results\COMPARISON_RESULTS.md"
    echo.
    echo =============================================================================
    echo RESULTS REPORT LOCATION
    echo =============================================================================
    echo.
    echo Markdown report saved to:
    echo   C:\Users\aya.alaswad\remote\MyReasearch\raddino_results\COMPARISON_RESULTS.md
    echo.
    echo JSON results saved to:
    echo   C:\Users\aya.alaswad\remote\MyReasearch\raddino_results\comparison.json
    echo.
    echo Open the markdown file to see:
    echo   - CheXbert F1 comparison
    echo   - Interpretation and recommendations
    echo   - Whether to include in paper
    echo.
) else (
    echo.
    echo [WARNING] Results extraction had errors
    echo          Check output above for details
    call write_progress.bat "WARNING: Results extraction had errors"
    echo.
)

echo [%DATE% %TIME%] Analysis complete >> stage2_training\logs\raddino_master.log

echo =============================================================================
echo.

pause
