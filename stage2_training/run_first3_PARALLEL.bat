@echo off
REM Stage 2: Fine-tune first 3 experiments IN PARALLEL (while Exp4 Stage 1 still running)
REM CAUTION: This runs while Exp4 Stage 1 is training!
REM Total time: ~2 hours

echo ========================================
echo Stage 2 Fine-Tuning - FIRST 3 PARALLEL
echo ========================================
echo.
echo CAUTION: This runs while Exp4 Stage 1 is still training!
echo.
echo GPU Usage:
echo   - Exp4 Stage 1 (batch=512): ~18GB
echo   - 3 Stage 2 experiments: ~9-12GB
echo   - Total: ~27-30GB / 32GB
echo.
echo This is TIGHT but should work!
echo.
echo Check current GPU usage:
nvidia-smi
echo.
pause

REM Create logs directory if it doesn't exist
mkdir ..\stage2_training\logs 2>nul

REM Launch first 3 experiments in parallel
cd C:\Users\aya.alaswad\remote\cxrmate

echo.
echo ========================================
echo [%TIME%] Launching first 3 experiments...
echo ========================================

REM Experiment 1
start "EXP1-Baseline" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp1_baseline.yaml --stages_module tools.stages --train > ..\stage2_training\logs\exp1_train.log 2>&1"
echo [%TIME%] Started Experiment 1: Baseline

timeout /t 5 /nobreak >nul

REM Experiment 2
start "EXP2-Paired" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp2_paired.yaml --stages_module tools.stages --train > ..\stage2_training\logs\exp2_train.log 2>&1"
echo [%TIME%] Started Experiment 2: Paired Sampling

timeout /t 5 /nobreak >nul

REM Experiment 3
start "EXP3-Full" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp3_full.yaml --stages_module tools.stages --train > ..\stage2_training\logs\exp3_train.log 2>&1"
echo [%TIME%] Started Experiment 3: Full SHARP

echo.
echo ========================================
echo First 3 experiments launched!
echo ========================================
echo.
echo Exp4 Stage 2 will run separately after Exp4 Stage 1 completes.
echo.
echo Monitor GPU usage:
echo   nvidia-smi
echo.
echo Monitor logs:
echo   powershell Get-Content ..\stage2_training\logs\exp1_train.log -Wait -Tail 20
echo   powershell Get-Content ..\stage2_training\logs\exp2_train.log -Wait -Tail 20
echo   powershell Get-Content ..\stage2_training\logs\exp3_train.log -Wait -Tail 20
echo.
echo If you see CUDA OUT OF MEMORY errors:
echo   1. Stop all: taskkill /F /IM python.exe
echo   2. Wait for Exp4 Stage 1 to finish
echo   3. Use run_all_experiments_PARALLEL.bat instead
echo.
echo Expected completion: ~2 hours
echo.
pause
