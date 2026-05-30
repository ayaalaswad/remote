@echo off
REM Stage 2 Training for Exp #4 v2a (Fair Matched-Epoch Large Batch)
REM
REM Stage 1 Result: 8.77% R@1 (BEST so far!)
REM Checkpoint: D:\experiments\exp4_v2a_matched_epochs\p3_best.pt
REM
REM This will fine-tune CXRMate for report generation and compute CheXbert F1
REM metrics to answer reviewer questions about downstream performance.
REM
REM Expected runtime: ~20 hours (32 epochs × ~40 min/epoch)
REM Output: experiments\cxrmate\single_tf\trial_2\

echo ============================================================================
echo Stage 2 Training - Exp #4 v2a (Fair Large Batch)
echo ============================================================================
echo.
echo Stage 1 Result: 8.77%% R@1 (BEST performance!)
echo Checkpoint: D:\experiments\exp4_v2a_matched_epochs\p3_best.pt
echo.
echo Configuration:
echo   - Model: CXRMate single-image report generation
echo   - Training: 32 epochs, batch=8, accumulated_batch=32
echo   - Validation: CheXbert F1 macro computed every epoch
echo   - Output: experiments\cxrmate\single_tf\trial_2\
echo.
echo Expected runtime: ~20 hours
echo.
pause

cd C:\Users\aya.alaswad\remote\cxrmate

dlhpcstarter -t cxrmate -c config/train/single_tf --stages_module tools.stages --train --trial 2 vit_ckpt_path=D:/experiments/exp4_v2a_matched_epochs/p3_best.pt

echo.
echo ============================================================================
echo Training complete!
echo ============================================================================
echo.
echo Results saved to: experiments\cxrmate\single_tf\trial_2\
echo.
echo To check CheXbert F1 results:
echo   cd experiments\cxrmate\single_tf\trial_2
echo   powershell -Command "Import-Csv lightning_logs\version_0\metrics.csv | Where-Object {$_.val_report_chexbert_f1_macro -ne ''} | Select-Object epoch, val_report_chexbert_f1_macro"
echo.
pause
