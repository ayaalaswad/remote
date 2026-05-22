@echo off
REM Stage 2: Test all 4 experiments IN PARALLEL
REM Total time: ~30 minutes (instead of 2 hours sequential)

echo ========================================
echo Stage 2 Testing - PARALLEL MODE
echo ========================================
echo.
echo This will test all 4 experiments simultaneously!
echo.
echo GPU Usage: ~4GB (much lighter than training)
echo Expected time: ~30 minutes
echo.
pause

REM Create logs directory if it doesn't exist
mkdir ..\stage2_training\logs 2>nul

REM Launch all 4 tests in parallel
cd C:\Users\aya.alaswad\remote\cxrmate

echo.
echo ========================================
echo [%TIME%] Launching all 4 tests...
echo ========================================

REM Test 1
start "TEST1-Baseline" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp1_baseline.yaml --stages_module tools.stages --test > ..\stage2_training\logs\exp1_test.log 2>&1"
echo [%TIME%] Started Test 1: Baseline

timeout /t 5 /nobreak >nul

REM Test 2
start "TEST2-Paired" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp2_paired.yaml --stages_module tools.stages --test > ..\stage2_training\logs\exp2_test.log 2>&1"
echo [%TIME%] Started Test 2: Paired Sampling

timeout /t 5 /nobreak >nul

REM Test 3
start "TEST3-Full" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp3_full.yaml --stages_module tools.stages --test > ..\stage2_training\logs\exp3_test.log 2>&1"
echo [%TIME%] Started Test 3: Full SHARP

timeout /t 5 /nobreak >nul

REM Test 4
start "TEST4-Large" /MIN cmd /c "python -m dlhpcstarter -t cxrmate -c ..\stage2_training\configs\exp4_large.yaml --stages_module tools.stages --test > ..\stage2_training\logs\exp4_test.log 2>&1"
echo [%TIME%] Started Test 4: Large Batch

echo.
echo ========================================
echo All 4 tests launched in parallel!
echo ========================================
echo.
echo Monitor logs:
echo   powershell Get-Content ..\stage2_training\logs\exp1_test.log -Wait -Tail 20
echo   powershell Get-Content ..\stage2_training\logs\exp2_test.log -Wait -Tail 20
echo   powershell Get-Content ..\stage2_training\logs\exp3_test.log -Wait -Tail 20
echo   powershell Get-Content ..\stage2_training\logs\exp4_test.log -Wait -Tail 20
echo.
echo Expected completion: ~30 minutes
echo.
echo After all complete, run:
echo   python extract_results.py
echo   python per_condition_analysis.py
echo.
pause
