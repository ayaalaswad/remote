@echo off
REM Setup CheXbert checkpoint for CXRMate validation
REM Run this on the REMOTE DESKTOP (C:\Users\aya.alaswad\remote)

echo ========================================
echo CheXbert Checkpoint Setup
echo ========================================
echo.
echo CXRMate expects checkpoint at:
echo   C:\Users\aya.alaswad\remote\checkpoints\stanford\chexbert\chexbert.pth
echo.

REM Change to CXRMate directory
cd /d C:\Users\aya.alaswad\remote\cxrmate

echo Step 1: Searching for existing chexbert.pth file...
echo.
dir /s /b C:\Users\aya.alaswad\*.pth 2>nul | findstr /i chexbert
if errorlevel 1 (
    echo No chexbert.pth found in user directory
) else (
    echo Found chexbert file(s) above
)
echo.

dir /s /b D:\*.pth 2>nul | findstr /i chexbert
if errorlevel 1 (
    echo No chexbert.pth found on D: drive
) else (
    echo Found chexbert file(s) above
)
echo.

echo Step 2: Checking target directory...
if not exist "checkpoints" (
    echo Creating checkpoints directory...
    mkdir checkpoints
)

if not exist "checkpoints\stanford" (
    echo Creating checkpoints\stanford directory...
    mkdir checkpoints\stanford
)

if not exist "checkpoints\stanford\chexbert" (
    echo Creating checkpoints\stanford\chexbert directory...
    mkdir checkpoints\stanford\chexbert
)

if exist "checkpoints\stanford\chexbert\chexbert.pth" (
    echo.
    echo ✓ Checkpoint already exists!
    dir "checkpoints\stanford\chexbert\chexbert.pth"
    echo.
    echo Training can continue.
) else (
    echo.
    echo ✗ Checkpoint does NOT exist at target location
    echo.
    echo TO DOWNLOAD:
    echo   1. Go to: https://github.com/stanfordmlgroup/CheXbert#checkpoint-download
    echo   2. Download chexbert.pth (approx 1.22 GB)
    echo   3. Place it at: checkpoints\stanford\chexbert\chexbert.pth
    echo.
    echo OR if you already downloaded it, copy it manually:
    echo   copy "path\to\your\chexbert.pth" "checkpoints\stanford\chexbert\"
    echo.
)

pause
