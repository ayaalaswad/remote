@echo off
REM Check what CXRMate single.py is actually looking for

echo Showing lines 280-290 from CXRMate single.py (where the error occurs):
echo.

type C:\Users\aya.alaswad\remote\cxrmate\modules\lightning_modules\single.py | findstr /N "." | findstr "28[0-9]:"

echo.
echo.
echo Searching for how dataset_dir is used:
echo.

findstr /N /C:"dataset_dir" /C:"split" /C:".csv" C:\Users\aya.alaswad\remote\cxrmate\modules\lightning_modules\single.py | findstr /R "27[0-9]: 28[0-9]: 29[0-9]:"

echo.
pause
