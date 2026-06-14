@echo off
REM ============================================================================
REM Push RSNA Linear Probe Results to GitHub
REM ============================================================================

echo ========================================
echo   Push RSNA Linear Probe Results
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote

REM Create results directory if it doesn't exist
if not exist "rsna_lp_results" mkdir rsna_lp_results

echo Copying results (excluding .pth checkpoints)...
echo.

REM Try different possible paths
set LP_DIR=BenchX\experiments\classification\rsna\SHARP_LP\SHARP_LinearProbe
if not exist "%LP_DIR%" set LP_DIR=BenchX\experiments\classification\rsna\SHARP_LP
if not exist "%LP_DIR%" set LP_DIR=BenchX\experiments\classification\rsna\SHARP_LP\SHARP_LP

if not exist "%LP_DIR%" (
    echo [ERROR] Linear Probe results not found!
    echo Searched paths:
    echo - BenchX\experiments\classification\rsna\SHARP_LP\SHARP_LinearProbe
    echo - BenchX\experiments\classification\rsna\SHARP_LP
    echo - BenchX\experiments\classification\rsna\SHARP_LP\SHARP_LP
    echo.
    pause
    exit /b 1
)

REM Copy logs
echo Copying logs...
xcopy "%LP_DIR%\*.log" "rsna_lp_results\" /Y /I >nul 2>&1

REM Copy metrics
echo Copying metrics...
xcopy "%LP_DIR%\*.txt" "rsna_lp_results\" /Y /I >nul 2>&1
xcopy "%LP_DIR%\*.json" "rsna_lp_results\" /Y /I >nul 2>&1

REM List checkpoints (don't copy .pth files - too large)
echo Listing checkpoints...
dir "%LP_DIR%\*.pth" /b >nul 2>&1
if not errorlevel 1 (
    dir "%LP_DIR%\*.pth" /b > "rsna_lp_results\checkpoints.txt"
)

echo.
echo [OK] Results copied
echo.

REM Add to git
echo Adding to git...
git add rsna_lp_results/

REM Also add config files
git add sharp_rsna_lp.yml sharp_rsna_10pct_lp.yml 2>nul
git add LINEAR_PROBE_COMPARISON.md 2>nul

REM Commit
echo.
echo Committing...
git status

git commit -m "Add RSNA Linear Probe results (frozen encoder)"

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
echo Linear Probe results pushed to GitHub.
echo Location: rsna_lp_results/
echo.

pause
