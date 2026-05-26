@echo off
REM Run Stage 2 Training - Exp #1 then Exp #3 (FIXED VERSION)
echo ========================================
echo Stage 2 Training Setup
echo ========================================
echo.

cd /d C:\Users\aya.alaswad\remote

echo Step 1: Copying config files to CXRMate config directory...
copy stage2_training\configs\exp1_baseline.yaml cxrmate\config\train\exp1_baseline.yaml /Y
copy stage2_training\configs\exp3_full.yaml cxrmate\config\train\exp3_full.yaml /Y

echo.
echo Config files copied!
echo.

cd cxrmate

echo Step 2: Starting Exp #1 Baseline training...
echo Command: dlhpcstarter -t cxrmate --config_dir config/train -c exp1_baseline --stages_module tools.stages --train --trial 0
echo.

dlhpcstarter -t cxrmate --config_dir config/train -c exp1_baseline --stages_module tools.stages --train --trial 0

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

dlhpcstarter -t cxrmate --config_dir config/train -c exp3_full --stages_module tools.stages --train --trial 0

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

pause
