@echo off
REM Stage 2 Training for Exp #2 (Forced Paired Sampling - COLLAPSED)
REM
REM Stage 1 Result: 0.81% R@1 (COLLAPSED due to 100% co-positive pairing)
REM Checkpoint: D:\experiments\exp2_paired\p3_best.pt
REM
REM CRITICAL FOR REBUTTAL: This confirms the collapse propagates to downstream.
REM If Stage 2 CheXbert F1 is also very low, this is the strongest evidence
REM for R3's question about co-positive frequency effects.
REM
REM Expected: Very low CheXbert F1 (if collapse propagates)
REM Expected runtime: ~20 hours (32 epochs × ~40 min/epoch)
REM Output: experiments\cxrmate\single_tf\trial_3\

echo ============================================================================
echo Stage 2 Training - Exp #2 (Forced Paired Sampling - COLLAPSED)
echo ============================================================================
echo.
echo Stage 1 Result: 0.81%% R@1 (COLLAPSED - 100%% co-positive pairing)
echo Checkpoint: D:\experiments\exp2_paired\p3_best.pt
echo.
echo CRITICAL FOR REBUTTAL:
echo   This experiment tests if the Stage 1 collapse propagates to downstream.
echo   Exp #2 had forced 100%% co-positive pairing and collapsed to 0.81%% R@1.
echo   If downstream CheXbert F1 is also very low, this proves the collapse
echo   affects clinical report generation, not just retrieval.
echo.
echo Configuration:
echo   - Model: CXRMate single-image report generation
echo   - Training: 32 epochs, batch=8, accumulated_batch=32
echo   - Validation: CheXbert F1 macro computed every epoch
echo   - Output: experiments\cxrmate\single_tf\trial_3\
echo.
echo Expected: Very low CheXbert F1 (confirming downstream collapse)
echo Expected runtime: ~20 hours
echo.
pause

cd C:\Users\aya.alaswad\remote\cxrmate

dlhpcstarter -t cxrmate -c config/train/single_tf --stages_module tools.stages --train --trial 3 vit_ckpt_path=D:/experiments/exp2_paired/p3_best.pt

echo.
echo ============================================================================
echo Training complete!
echo ============================================================================
echo.
echo Results saved to: experiments\cxrmate\single_tf\trial_3\
echo.
echo To check CheXbert F1 results:
echo   cd experiments\cxrmate\single_tf\trial_3
echo   powershell -Command "Import-Csv lightning_logs\version_0\metrics.csv | Where-Object {$_.val_report_chexbert_f1_macro -ne ''} | Select-Object epoch, val_report_chexbert_f1_macro | Select-Object -Last 10"
echo.
echo EXPECTED: If F1 is very low (e.g., under 20%%), collapse propagated to downstream.
echo           This is STRONG evidence for the rebuttal.
echo.
pause
