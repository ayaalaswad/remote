@echo off
REM ============================================================================
REM Push RSNA Results to GitHub (Exclude .pt checkpoints)
REM ============================================================================

echo ========================================
echo   Push RSNA Results to GitHub
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote

REM Create results directory if it doesn't exist
if not exist "rsna_results_latest" mkdir rsna_results_latest

REM Copy all results folders (excluding .pt files)
echo Copying results (excluding .pt checkpoints)...
echo.

REM Copy each folder's logs and metrics (exclude .pt files)
REM Use /S flag to search subdirectories (handles nested folder structure)
for /D %%D in (BenchX\experiments\classification\rsna\*) do (
    echo Copying %%~nxD...

    if not exist "rsna_results_latest\%%~nxD" mkdir "rsna_results_latest\%%~nxD"

    REM Copy .log files (search subdirectories)
    xcopy "%%D\*.log" "rsna_results_latest\%%~nxD\" /Y /Q /S 2>nul

    REM Copy .txt files (search subdirectories)
    xcopy "%%D\*.txt" "rsna_results_latest\%%~nxD\" /Y /Q /S 2>nul

    REM Copy .json files (search subdirectories)
    xcopy "%%D\*.json" "rsna_results_latest\%%~nxD\" /Y /Q /S 2>nul

    REM Skip .pt and .pth files (they're huge)
)

echo.
echo [OK] Results copied
echo.

REM Add to git
echo Adding to git...
git add rsna_results_latest/
echo.

REM Commit
echo Committing...
git commit -m "Add RSNA results (all checkpoints, excluding .pt files)

Results from all RSNA experiments:
- SHARP (original Exp #3)
- SHARP_1pct, SHARP_10pct, SHARP_100pct (3 data regimes)
- SHARP_EXP1_10pct (Exp #1 baseline checkpoint)
- SHARP_EXP4v2a_10pct (Exp #4 v2a, best R@1 checkpoint)

Checkpoint files (.pt) excluded to save space.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

if errorlevel 1 (
    echo.
    echo [WARNING] Commit failed - might be nothing to commit
    echo.
)

REM Push
echo Pushing to GitHub...
git push origin main

if errorlevel 1 (
    echo.
    echo [ERROR] Push failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Results Pushed Successfully!
echo ========================================
echo.
echo You can now pull these results on the other machine.
echo Location: rsna_results_latest/
echo.

pause
