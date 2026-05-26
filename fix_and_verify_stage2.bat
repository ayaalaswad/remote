@echo off
REM All-in-one script: Fix all Stage 2 paths and verify
REM Run this ONCE on remote desktop, then you're ready to train

echo ========================================
echo Stage 2 Setup - Fix and Verify
echo ========================================
echo.

cd /d C:\Users\aya.alaswad\remote\cxrmate

echo Step 1: Fixing CheXbert checkpoint path...
echo.

REM Check if checkpoints directory is a junction or regular directory
dir checkpoints | find "<JUNCTION>" > nul 2>&1
if %errorlevel% == 0 (
    echo checkpoints is already a junction - good!
    goto :verify
)

REM Check if checkpoints directory exists and is NOT a junction
if exist checkpoints (
    echo checkpoints directory exists but is NOT a junction
    echo Checking what's inside...
    dir /s /b checkpoints\*.pth 2>nul

    echo.
    echo Renaming existing checkpoints to checkpoints_old...
    ren checkpoints checkpoints_old
    if errorlevel 1 (
        echo ERROR: Could not rename checkpoints directory
        echo Please close any programs using files in checkpoints directory
        pause
        exit /b 1
    )
)

REM Create junction to parent checkpoints directory
echo Creating junction: checkpoints -^> C:\Users\aya.alaswad\remote\checkpoints
mklink /J checkpoints C:\Users\aya.alaswad\remote\checkpoints
if errorlevel 1 (
    echo ERROR: Could not create junction
    echo Restoring original checkpoints directory...
    if exist checkpoints_old ren checkpoints_old checkpoints
    pause
    exit /b 1
)

echo Junction created successfully!
echo.

:verify
echo Step 2: Verifying all paths...
echo ========================================
echo.

set ALL_GOOD=1

REM 1. CheXbert checkpoint
echo [1] CheXbert checkpoint:
if exist "checkpoints\stanford\chexbert\chexbert.pth" (
    echo     OK - checkpoints\stanford\chexbert\chexbert.pth
    for %%A in ("checkpoints\stanford\chexbert\chexbert.pth") do echo          Size: %%~zA bytes
) else (
    echo     MISSING - checkpoints\stanford\chexbert\chexbert.pth
    set ALL_GOOD=0
)
echo.

REM 2. Stage 1 checkpoints
echo [2] Stage 1 ViT checkpoints:
if exist "D:\experiments\exp1_baseline\p3_best.pt" (
    echo     OK - Exp #1: D:\experiments\exp1_baseline\p3_best.pt
    for %%A in ("D:\experiments\exp1_baseline\p3_best.pt") do echo          Size: %%~zA bytes
) else (
    echo     MISSING - D:\experiments\exp1_baseline\p3_best.pt
    set ALL_GOOD=0
)

if exist "D:\experiments\exp3_full_sharp\p3_best.pt" (
    echo     OK - Exp #3: D:\experiments\exp3_full_sharp\p3_best.pt
    for %%A in ("D:\experiments\exp3_full_sharp\p3_best.pt") do echo          Size: %%~zA bytes
) else (
    echo     MISSING - D:\experiments\exp3_full_sharp\p3_best.pt
    set ALL_GOOD=0
)
echo.

REM 3. Dataset CSV files
echo [3] Dataset CSV files:
if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-split.csv.gz" (
    echo     OK - mimic-cxr-2.0.0-split.csv.gz
) else (
    echo     MISSING - mimic-cxr-2.0.0-split.csv.gz
    set ALL_GOOD=0
)

if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-metadata.csv.gz" (
    echo     OK - mimic-cxr-2.0.0-metadata.csv.gz
) else (
    echo     MISSING - mimic-cxr-2.0.0-metadata.csv.gz
    set ALL_GOOD=0
)

if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic_cxr_sections\mimic_cxr_sectioned.csv" (
    echo     OK - mimic_cxr_sections\mimic_cxr_sectioned.csv
) else (
    echo     MISSING - mimic_cxr_sections\mimic_cxr_sectioned.csv
    set ALL_GOOD=0
)
echo.

echo ========================================
echo FINAL RESULT
echo ========================================
echo.

if %ALL_GOOD% == 1 (
    echo *** ALL CHECKS PASSED ***
    echo.
    echo You are READY to run Stage 2 training!
    echo.
    echo To start Exp #1 Baseline:
    echo   python train.py --config_path "C:\Users\ZA\lawer\MyReasearch\stage2_training\configs\exp1_baseline.yaml"
    echo.
    echo To start Exp #3 Full:
    echo   python train.py --config_path "C:\Users\ZA\lawer\MyReasearch\stage2_training\configs\exp3_full.yaml"
    echo.
) else (
    echo *** SOME CHECKS FAILED ***
    echo.
    echo DO NOT start training yet - there are missing files.
    echo Copy this output and send it to continue troubleshooting.
    echo.
)

pause
