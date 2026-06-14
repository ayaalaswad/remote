@echo off
REM ============================================================================
REM Push RadDINO Hard Negatives Results to GitHub
REM ============================================================================

echo ========================================
echo   Push RadDINO Results
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote

REM Create results directory if it doesn't exist
if not exist "raddino_results" mkdir raddino_results

echo Copying results (excluding large .pt checkpoints)...
echo.

set RADDINO_DIR=D:\experiments\exp_raddino_hardneg

if not exist "%RADDINO_DIR%" (
    echo [ERROR] RadDINO results not found!
    echo.
    pause
    exit /b 1
)

REM Copy logs and history
echo Copying training logs...
xcopy "%RADDINO_DIR%\*.log" "raddino_results\" /Y /I >nul 2>&1
xcopy "%RADDINO_DIR%\*.json" "raddino_results\" /Y /I >nul 2>&1
xcopy "%RADDINO_DIR%\*.txt" "raddino_results\" /Y /I >nul 2>&1

REM Create summary of checkpoints (don't copy .pt files - too large)
echo Listing checkpoints...
dir "%RADDINO_DIR%\*.pt" /b >nul 2>&1
if not errorlevel 1 (
    dir "%RADDINO_DIR%\*.pt" /b > "raddino_results\checkpoints.txt"
)

REM Create results summary
echo Creating results summary...
echo RadDINO Hard Negatives Training Results > "raddino_results\SUMMARY.txt"
echo ========================================== >> "raddino_results\SUMMARY.txt"
echo. >> "raddino_results\SUMMARY.txt"
echo Training completed at step 88,000 (early stopping) >> "raddino_results\SUMMARY.txt"
echo Best I-^>T R@1: 10.26%% (at step 32,000) >> "raddino_results\SUMMARY.txt"
echo. >> "raddino_results\SUMMARY.txt"
echo Configuration: >> "raddino_results\SUMMARY.txt"
echo - Batch size: 256 >> "raddino_results\SUMMARY.txt"
echo - Hard negatives enabled >> "raddino_results\SUMMARY.txt"
echo - Early stopping: 10 evals without improvement >> "raddino_results\SUMMARY.txt"
echo. >> "raddino_results\SUMMARY.txt"
echo Best checkpoint: D:\experiments\exp_raddino_hardneg\p3_best.pt >> "raddino_results\SUMMARY.txt"
echo Last checkpoint: D:\experiments\exp_raddino_hardneg\p3_last.pt >> "raddino_results\SUMMARY.txt"
echo. >> "raddino_results\SUMMARY.txt"

echo.
echo [OK] Results copied
echo.

REM Add to git
echo Adding to git...
git add raddino_results/

REM Also add config files
git add raddino_*.yml 2>nul

REM Commit
echo.
echo Committing...
git status

git commit -m "Add RadDINO hard negatives training results (R@1: 10.26%%)"

if errorlevel 1 (
    echo.
    echo [WARNING] Commit failed - might be nothing to commit
    echo.
)

REM Push
echo.
echo Pushing to GitHub...
git push origin main

if errorlevel 1 (
    echo.
    echo [ERROR] Push failed! Check error above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Results Pushed Successfully!
echo ========================================
echo.
echo RadDINO results pushed to GitHub.
echo Location: raddino_results/
echo.

pause
