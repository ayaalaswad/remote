@echo off
REM Verify Exp #4 v2a Stage 1 Results (8.77% R@1)
REM
REM Sanity check before staking rebuttal on this number.
REM 8.77% is a significant jump from baseline (6.61%), so verify:
REM   1. It's from p3_best.pt (not p3_last.pt)
REM   2. Training was stable (no loss spikes or collapse)
REM   3. R@1 progression makes sense
REM
REM Runtime: ~5 minutes (mostly reading logs)

echo ============================================================================
echo Verifying Exp #4 v2a Stage 1 Results (8.77%% R@1)
echo ============================================================================
echo.
echo Checking if 8.77%% R@1 is reliable before using in rebuttal.
echo A jump from 6.61%% (baseline) to 8.77%% is large - must verify!
echo.

cd D:\experiments\exp4_v2a_matched_epochs

echo ============================================================================
echo [1/4] Checking Checkpoint Files
echo ============================================================================
echo.

if exist p3_best.pt (
    echo OK - p3_best.pt exists
    for %%A in (p3_best.pt) do echo    Size: %%~zA bytes
) else (
    echo ERROR - p3_best.pt NOT FOUND!
    echo Cannot verify results without checkpoint.
    pause
    exit /b 1
)

if exist p3_last.pt (
    echo OK - p3_last.pt exists
    for %%A in (p3_last.pt) do echo    Size: %%~zA bytes
) else (
    echo WARNING - p3_last.pt not found
)

echo.
echo Checkpoint files look good.
echo.

echo ============================================================================
echo [2/4] Checking Training Stability (Loss Curve)
echo ============================================================================
echo.

if exist training.log (
    echo Extracting loss values from training log...
    findstr /C:"loss=" training.log | findstr /C:"R@1=" > loss_curve.txt
    echo.
    echo Last 20 training steps (check for spikes or collapse):
    powershell -Command "Get-Content loss_curve.txt | Select-Object -Last 20"
    echo.
    echo Saved full loss curve to: loss_curve.txt
) else (
    echo ERROR - training.log not found!
    echo Cannot verify training stability.
)

echo.

echo ============================================================================
echo [3/4] Checking R@1 Progression Across Evaluations
echo ============================================================================
echo.

if exist training.log (
    echo Extracting all R@1 evaluation results...
    findstr /C:"I->T R@1=" training.log | findstr /C:"step" > r1_progression.txt
    echo.
    echo R@1 progression (all eval points):
    type r1_progression.txt
    echo.
    echo Saved to: r1_progression.txt
    echo.
    echo Checking for best R@1...
    findstr /C:"Best I->T R@1" training.log
) else (
    echo ERROR - Cannot extract R@1 progression
)

echo.

echo ============================================================================
echo [4/4] Verification Summary
echo ============================================================================
echo.

findstr /C:"Best I->T R@1" training.log
echo.
echo From training log: Best R@1 should be 8.77%%
echo From checkpoint: p3_best.pt saved at best R@1
echo.
echo Manual checks:
echo   1. Does R@1 progression in r1_progression.txt show steady improvement?
echo   2. Does loss curve in loss_curve.txt show no spikes or collapse?
echo   3. Is final R@1 (8.77%%) consistent across multiple eval points?
echo.

echo ============================================================================
echo Additional Verification (Optional)
echo ============================================================================
echo.
echo To re-run evaluation with the same script as Exp #1 (confirms number):
echo   1. Check how Exp #1 eval was run
echo   2. Run same eval script on Exp #4 v2a checkpoint
echo   3. Confirm R@1 matches 8.77%%
echo.
echo This is OPTIONAL - only needed if you see irregularities above.
echo.

cd C:\Users\aya.alaswad\remote

echo ============================================================================
echo Verification Complete
echo ============================================================================
echo.
echo Files created in D:\experiments\exp4_v2a_matched_epochs\:
echo   - loss_curve.txt (check for stability)
echo   - r1_progression.txt (check R@1 improvement pattern)
echo.
echo Review these files. If training looks stable and R@1 progression is
echo smooth, then 8.77%% is reliable for the rebuttal.
echo.
echo If you see issues (spikes, collapse, inconsistent R@1), investigate further
echo before using this number in the rebuttal.
echo.
pause
