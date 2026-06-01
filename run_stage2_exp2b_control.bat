@echo off
REM Stage 2 Training for Exp #2b (20k Random Control)
REM
REM Stage 1 Result: 4.99% R@1 (20k files, natural ~37% co-positive pairing)
REM Checkpoint: D:\experiments\exp2b_20k_random\p3_best.pt
REM
REM CRITICAL FOR REBUTTAL: This controls for dataset size effects.
REM Exp #2 used 20k files + forced pairing → 0.81% R@1
REM Exp #2b uses 20k files + natural pairing → 4.99% R@1
REM
REM If Exp #2b Stage 2 CheXbert F1 is reasonable (e.g., 25-30%), this proves:
REM   - 20k files is sufficient for downstream
REM   - The collapse (Exp #2) was due to FORCED PAIRING, not dataset size
REM
REM Expected: Moderate CheXbert F1 (between Exp #2 and Exp #1)
REM Expected runtime: ~20 hours (32 epochs × ~40 min/epoch)
REM Output: experiments\cxrmate\single_tf\trial_4\

echo ============================================================================
echo Stage 2 Training - Exp #2b (20k Random Control)
echo ============================================================================
echo.
echo Stage 1 Result: 4.99%% R@1 (20k files, natural pairing)
echo Checkpoint: D:\experiments\exp2b_20k_random\p3_best.pt
echo.
echo CRITICAL FOR REBUTTAL:
echo   This experiment controls for dataset size at downstream level.
echo
echo   Comparison:
echo     - Exp #2:  20k files + forced pairing → 0.81%% R@1, [TBD] F1
echo     - Exp #2b: 20k files + natural pairing → 4.99%% R@1, [TBD] F1
echo     - Exp #1:  60k+ files + natural pairing → 6.61%% R@1, 31.2%% F1
echo.
echo   If Exp #2b gets reasonable F1 (25-30%%), this proves the collapse
echo   was due to forced pairing, NOT dataset size reduction.
echo.
echo Configuration:
echo   - Model: CXRMate single-image report generation
echo   - Training: 32 epochs, batch=8, accumulated_batch=32
echo   - Validation: CheXbert F1 macro computed every epoch
echo   - Output: experiments\cxrmate\single_tf\trial_4\
echo.
echo Expected: Moderate CheXbert F1 (proves 20k sufficient for downstream)
echo Expected runtime: ~20 hours
echo.
pause

cd C:\Users\aya.alaswad\remote\cxrmate

dlhpcstarter -t cxrmate -c config/train/single_tf --stages_module tools.stages --train --trial 4 vit_ckpt_path=D:/experiments/exp2b_20k_random/p3_best.pt

echo.
echo ============================================================================
echo Training complete!
echo ============================================================================
echo.
echo Results saved to: experiments\cxrmate\single_tf\trial_4\
echo.
echo To check CheXbert F1 results:
echo   cd experiments\cxrmate\single_tf\trial_4
echo   powershell -Command "Import-Csv lightning_logs\version_0\metrics.csv | Where-Object {$_.val_report_chexbert_f1_macro -ne ''} | Select-Object epoch, val_report_chexbert_f1_macro | Select-Object -Last 10"
echo.
echo EXPECTED: If F1 is moderate (25-30%%), dataset size is NOT the issue.
echo           This proves forced pairing (not dataset size) caused collapse.
echo.
pause
