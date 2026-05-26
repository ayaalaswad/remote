@echo off
REM Check CXRMate single.py to see what it expects

echo Checking CXRMate code for path expectations...
echo.

REM Show lines around line 285 where the error occurs
echo ===== single.py around line 285 =====
type C:\Users\aya.alaswad\remote\cxrmate\modules\lightning_modules\single.py | findstr /N "." | findstr "28[0-9]:"
echo.

REM Search for where it looks for CSV files
echo ===== Searching for CSV file paths =====
findstr /N /C:"split" /C:".csv" /C:"dataset_dir" C:\Users\aya.alaswad\remote\cxrmate\modules\lightning_modules\single.py | findstr /R "27[0-9]: 28[0-9]: 29[0-9]:"
echo.

pause
