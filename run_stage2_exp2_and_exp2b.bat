@echo off
REM Run BOTH Exp #2 and Exp #2b Stage 2 Training (Sequential)
REM
REM This script runs both critical missing experiments for the rebuttal:
REM   1. Exp #2 (forced pairing collapse) - confirms collapse propagates
REM   2. Exp #2b (20k random control) - controls for dataset size
REM
REM Total runtime: ~40 hours (20h each, sequential on 1 GPU)
REM
REM ALTERNATIVE: If you have 2 GPUs or want to run manually, use:
REM   - run_stage2_exp2_paired.bat (in one terminal)
REM   - run_stage2_exp2b_control.bat (in another terminal)

echo ============================================================================
echo Stage 2 Training - Exp #2 AND Exp #2b (Critical for Rebuttal)
echo ============================================================================
echo.
echo This will run TWO experiments sequentially:
echo.
echo 1. Exp #2 (Forced Pairing Collapse)
echo    - Stage 1: 0.81%% R@1 (collapsed)
echo    - Expected Stage 2: Very low CheXbert F1
echo    - Proves: Collapse propagates to downstream
echo    - Runtime: ~20 hours
echo.
echo 2. Exp #2b (20k Random Control)
echo    - Stage 1: 4.99%% R@1 (20k files, natural pairing)
echo    - Expected Stage 2: Moderate CheXbert F1 (25-30%%)
echo    - Proves: Dataset size is NOT the issue
echo    - Runtime: ~20 hours
echo.
echo TOTAL RUNTIME: ~40 hours (runs overnight + next day)
echo.
echo These are CRITICAL for answering R3's co-positive frequency question.
echo.
pause

echo.
echo ============================================================================
echo [1/2] Starting Exp #2 (Forced Pairing Collapse)...
echo ============================================================================
echo.

cd C:\Users\aya.alaswad\remote\cxrmate

dlhpcstarter -t cxrmate -c config/train/single_tf --stages_module tools.stages --train --trial 3 vit_ckpt_path=D:/experiments/exp2_paired/p3_best.pt

if errorlevel 1 (
    echo.
    echo ERROR: Exp #2 training failed!
    echo Check: experiments\cxrmate\single_tf\trial_3\
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo [1/2] Exp #2 Complete! Checking results...
echo ============================================================================
echo.

cd experiments\cxrmate\single_tf\trial_3
echo Best CheXbert F1 for Exp #2:
powershell -Command "Import-Csv lightning_logs\version_0\metrics.csv | Where-Object {$_.val_report_chexbert_f1_macro -ne ''} | Select-Object epoch, val_report_chexbert_f1_macro | Sort-Object {[double]$_.val_report_chexbert_f1_macro} -Descending | Select-Object -First 1"

cd C:\Users\aya.alaswad\remote\cxrmate

echo.
echo ============================================================================
echo [2/2] Starting Exp #2b (20k Random Control)...
echo ============================================================================
echo.

dlhpcstarter -t cxrmate -c config/train/single_tf --stages_module tools.stages --train --trial 4 vit_ckpt_path=D:/experiments/exp2b_20k_random/p3_best.pt

if errorlevel 1 (
    echo.
    echo ERROR: Exp #2b training failed!
    echo Check: experiments\cxrmate\single_tf\trial_4\
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo [2/2] Exp #2b Complete! Checking results...
echo ============================================================================
echo.

cd experiments\cxrmate\single_tf\trial_4
echo Best CheXbert F1 for Exp #2b:
powershell -Command "Import-Csv lightning_logs\version_0\metrics.csv | Where-Object {$_.val_report_chexbert_f1_macro -ne ''} | Select-Object epoch, val_report_chexbert_f1_macro | Sort-Object {[double]$_.val_report_chexbert_f1_macro} -Descending | Select-Object -First 1"

echo.
echo ============================================================================
echo ALL TRAINING COMPLETE!
echo ============================================================================
echo.
echo Exp #2 results: experiments\cxrmate\single_tf\trial_3\
echo Exp #2b results: experiments\cxrmate\single_tf\trial_4\
echo.
echo You now have ALL data needed for the rebuttal!
echo.
echo Next step: Extract per-condition CheXbert F1 for all experiments
echo.
pause
