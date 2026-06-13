@echo off
REM ============================================================================
REM Push SIIM Results to GitHub
REM ============================================================================

echo ========================================
echo   Push SIIM Results to GitHub
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote

REM Create results directory if it doesn't exist
if not exist "siim_results_latest" mkdir siim_results_latest

echo Copying results (excluding .pt checkpoints)...
echo.

REM Copy results from each experiment (excluding large .pth files)
for %%D in (SHARP SHARP_100pct SHARP_10pct SHARP_1pct SHARP_EXP1_10pct SHARP_EXP4v2a_10pct) do (
    if exist "BenchX\experiments\classification\siim\%%D" (
        echo Copying %%D...

        REM Create directory structure
        if not exist "siim_results_latest\%%D" mkdir "siim_results_latest\%%D"

        REM Copy logs
        xcopy "BenchX\experiments\classification\siim\%%D\*.log" "siim_results_latest\%%D\" /Y /I >nul 2>&1

        REM Copy metrics (txt, json)
        xcopy "BenchX\experiments\classification\siim\%%D\*\*.txt" "siim_results_latest\%%D\%%D\" /Y /I >nul 2>&1
        xcopy "BenchX\experiments\classification\siim\%%D\*\*.json" "siim_results_latest\%%D\%%D\" /Y /I >nul 2>&1

        REM Copy checkpoint info but not the actual .pth files (too large)
        dir "BenchX\experiments\classification\siim\%%D\*\*.pth" /b >nul 2>&1
        if not errorlevel 1 (
            dir "BenchX\experiments\classification\siim\%%D\*\*.pth" /b > "siim_results_latest\%%D\checkpoints.txt"
        )
    )
)

echo.
echo [OK] Results copied
echo.

REM Add to git
echo Adding to git...
git add siim_results_latest/

REM Also add any modified config files
git add sharp_*.yml 2>nul

REM Commit
echo.
echo Committing...
git status

git commit -m "Add SIIM BenchX results (1%%, 10%%, 100%%)"

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
echo You can now pull these results on the other machine.
echo Location: siim_results_latest/
echo.
pause
