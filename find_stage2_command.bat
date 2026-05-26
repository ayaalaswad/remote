@echo off
REM Find the exact command to run Stage 2 training
echo ========================================
echo Finding Stage 2 Training Command
echo ========================================
echo.

cd /d C:\Users\aya.alaswad\remote\cxrmate

echo [1] Checking config directory structure:
echo.
tree config /F
echo.
echo ========================================
echo.

echo [2] Looking for example scripts or documentation:
echo.
dir /s /b *.sh *.bat *.md 2>nul | findstr /i "train run example readme"
echo.
echo ========================================
echo.

echo [3] Checking for Python training scripts:
echo.
dir /s /b *.py 2>nul | findstr /i "train"
echo.
echo ========================================
echo.

echo [4] Checking last training log to see what command was used:
echo.
if exist "experiments" (
    echo Experiments directory exists
    dir /s /od experiments | find "Directory of" | more +1
    echo.
    echo Looking for log files...
    dir /s /b experiments\*.log experiments\*.txt 2>nul | more
) else (
    echo No experiments directory found
)
echo.
echo ========================================
echo.

echo [5] Checking if there's a setup or run script:
echo.
dir *.py *.sh *.bat 2>nul
echo.
echo ========================================
echo.

echo [6] Checking what's in tools directory:
echo.
dir tools\*.py 2>nul
echo.

pause
