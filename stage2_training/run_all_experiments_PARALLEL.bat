@echo off
REM Stage 2: Fine-tune CXRMate with all 4 checkpoints IN PARALLEL
REM IMPORTANT: Only run this AFTER Exp4 Stage 1 completes!
REM Total time: ~2 hours (instead of 8 hours sequential)

echo ========================================
echo Stage 2 Fine-Tuning - PARALLEL MODE
echo ========================================
echo.
echo WARNING: This will run all 4 experiments simultaneously!
echo.
echo GPU Usage:
echo   - 4 experiments x 3-4GB each = 12-16GB
echo   - Your RTX 5090 has 32GB VRAM
echo   - Should be safe!
echo.
echo Make sure Exp4 Stage 1 is FINISHED before running this!
echo Check: dir D:\experiments\exp4_large_batch\p3_best.pt
echo.
pause

REM Create logs directory if it doesn't exist
mkdir ..\stage2_training\logs 2>nul

REM Launch all 4 experiments in parallel using START command
cd C:\Users\aya.alaswad\remote\cxrmate

echo.
echo ========================================
echo [%TIME%] Launching all 4 experiments...
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

timeout /t 5 /nobreak >nul

REM Experiment 4
start "EXP4-Large" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp4_large.yaml --stages_module tools.stages --train > ..\stage2_training\logs\exp4_train.log 2>&1"
echo [%TIME%] Started Experiment 4: Large Batch

echo.
echo ========================================
echo All 4 experiments launched in parallel!
echo ========================================
echo.
echo They are running in minimized windows.
echo Check progress:
echo   - nvidia-smi (GPU usage)
echo   - tasklist ^| findstr python (see 4 python processes)
echo.
echo Monitor logs in real-time:
echo   powershell Get-Content ..\stage2_training\logs\exp1_train.log -Wait -Tail 20
echo   powershell Get-Content ..\stage2_training\logs\exp2_train.log -Wait -Tail 20
echo   powershell Get-Content ..\stage2_training\logs\exp3_train.log -Wait -Tail 20
echo   powershell Get-Content ..\stage2_training\logs\exp4_train.log -Wait -Tail 20
echo.
echo Expected completion: ~2 hours
echo.
echo After all complete, run: run_all_tests_PARALLEL.bat
echo.
pause
