@echo off
REM Find all experiment directories and their checkpoints

echo ========================================
echo Searching for Stage 1 Checkpoints
echo ========================================
echo.

echo Checking exp3_full_sharp details...
dir D:\experiments\exp3_full_sharp\*.pt
echo.

echo Checking for other experiment directories...
dir D:\experiments\exp1* /AD 2>nul
dir D:\experiments\exp2* /AD 2>nul
dir D:\experiments\exp4* /AD 2>nul
echo.

echo Checking experiment_config.json for training phases...
type D:\experiments\exp3_full_sharp\experiment_config.json
echo.

echo Checking if training.log mentions "contrastive" or "report generation"...
findstr /I /C:"contrastive" /C:"report" /C:"stage" D:\experiments\exp3_full_sharp\training.log | more
echo.

echo ========================================
echo Done
echo ========================================
