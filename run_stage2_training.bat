@echo off
REM Run Stage 2 Training - Exp #1 then Exp #3
echo ========================================
echo Stage 2 Training Setup
echo ========================================
echo.

cd /d C:\Users\aya.alaswad\remote

echo Step 1: Copying config files to CXRMate config directory...
copy stage2_training\configs\exp1_baseline.yaml cxrmate\config\train\exp1_baseline.yaml
if errorlevel 1 (
    echo ERROR: Could not copy exp1_baseline.yaml
    pause
    exit /b 1
)

copy stage2_training\configs\exp3_full.yaml cxrmate\config\train\exp3_full.yaml
if errorlevel 1 (
    echo ERROR: Could not copy exp3_full.yaml
    pause
    exit /b 1
)

echo.
echo Config files copied successfully!
echo.

cd cxrmate

echo Step 2: Starting Exp #1 Baseline training...
echo.
dlhpcstarter -t cxrmate -c exp1_baseline --stages_module tools.stages --train --trial 0
if errorlevel 1 (
    echo.
    echo ERROR: Exp #1 training failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Exp #1 Complete! Starting Exp #3...
echo ========================================
echo.

dlhpcstarter -t cxrmate -c exp3_full --stages_module tools.stages --train --trial 0
if errorlevel 1 (
    echo.
    echo ERROR: Exp #3 training failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo ALL TRAINING COMPLETE!
echo ========================================
echo.
echo Check results in: experiments\cxrmate\
echo.

pause
