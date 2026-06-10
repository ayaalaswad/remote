@echo off
REM ============================================================================
REM Push SHARP_EXP4v2a_10pct_AVG Results
REM ============================================================================

echo Pushing SHARP_EXP4v2a_10pct_AVG results...
echo.

cd C:\Users\aya.alaswad\remote

REM Create target directory
if not exist "rsna_results_latest\SHARP_EXP4v2a_10pct_AVG" mkdir "rsna_results_latest\SHARP_EXP4v2a_10pct_AVG"

REM Copy results from the AVG folder
echo Copying from: BenchX\experiments\classification\rsna\SHARP_EXP4v2a_10pct_AVG
echo.

xcopy "BenchX\experiments\classification\rsna\SHARP_EXP4v2a_10pct_AVG\*.log" "rsna_results_latest\SHARP_EXP4v2a_10pct_AVG\" /Y /Q /S 2>nul
xcopy "BenchX\experiments\classification\rsna\SHARP_EXP4v2a_10pct_AVG\*.txt" "rsna_results_latest\SHARP_EXP4v2a_10pct_AVG\" /Y /Q /S 2>nul
xcopy "BenchX\experiments\classification\rsna\SHARP_EXP4v2a_10pct_AVG\*.json" "rsna_results_latest\SHARP_EXP4v2a_10pct_AVG\" /Y /Q /S 2>nul

echo.
echo [OK] Files copied

REM Git operations
git config user.email "aya.alaswad@remote.com" 2>nul
git config user.name "Aya Alaswad" 2>nul

git add rsna_results_latest/SHARP_EXP4v2a_10pct_AVG/
git commit -m "Add SHARP Exp4v2a AVG pooling results (RSNA 10pct)"
git push origin main

echo.
echo [OK] Results pushed!
echo.
pause
