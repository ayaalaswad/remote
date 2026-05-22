@echo off
REM Stage 2: Test all 4 fine-tuned CXRMate models
REM Run this after run_all_experiments.bat completes
REM Total time: ~2 hours (30 min per experiment)

echo ========================================
echo Stage 2 Testing - All Experiments
echo ========================================
echo.
echo This will evaluate all 4 fine-tuned models on the test set
echo and measure CheXbert F1, RadGraph F1, and NLG metrics.
echo.
echo Total estimated time: 2 hours
echo.
pause

cd C:\Users\aya.alaswad\remote\cxrmate

REM Experiment 1: Baseline
echo.
echo ========================================
echo [%TIME%] Testing Experiment 1: Baseline
echo ========================================
python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp1_baseline.yaml ^
    --stages_module tools.stages ^
    --test ^
    > ..\stage2_training\logs\exp1_test.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Experiment 1 testing completed successfully
    echo Extracting key metrics...
    findstr /C:"test_report_chexbert_f1_macro" ..\stage2_training\logs\exp1_test.log
    findstr /C:"test_report_radgraph_f1" ..\stage2_training\logs\exp1_test.log
) else (
    echo [%TIME%] ERROR: Experiment 1 testing failed - check logs\exp1_test.log
    pause
    exit /b 1
)

REM Experiment 2: Paired Sampling
echo.
echo ========================================
echo [%TIME%] Testing Experiment 2: Paired Sampling
echo ========================================
python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp2_paired.yaml ^
    --stages_module tools.stages ^
    --test ^
    > ..\stage2_training\logs\exp2_test.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Experiment 2 testing completed successfully
    echo Extracting key metrics...
    findstr /C:"test_report_chexbert_f1_macro" ..\stage2_training\logs\exp2_test.log
    findstr /C:"test_report_radgraph_f1" ..\stage2_training\logs\exp2_test.log
) else (
    echo [%TIME%] ERROR: Experiment 2 testing failed - check logs\exp2_test.log
    pause
    exit /b 1
)

REM Experiment 3: Full SHARP
echo.
echo ========================================
echo [%TIME%] Testing Experiment 3: Full SHARP
echo ========================================
python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp3_full.yaml ^
    --stages_module tools.stages ^
    --test ^
    > ..\stage2_training\logs\exp3_test.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Experiment 3 testing completed successfully
    echo Extracting key metrics...
    findstr /C:"test_report_chexbert_f1_macro" ..\stage2_training\logs\exp3_test.log
    findstr /C:"test_report_radgraph_f1" ..\stage2_training\logs\exp3_test.log
) else (
    echo [%TIME%] ERROR: Experiment 3 testing failed - check logs\exp3_test.log
    pause
    exit /b 1
)

REM Experiment 4: Large Batch
echo.
echo ========================================
echo [%TIME%] Testing Experiment 4: Large Batch
echo ========================================
python -m dlhpcstarter ^
    -t cxrmate ^
    -c ..\stage2_training\configs\exp4_large.yaml ^
    --stages_module tools.stages ^
    --test ^
    > ..\stage2_training\logs\exp4_test.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Experiment 4 testing completed successfully
    echo Extracting key metrics...
    findstr /C:"test_report_chexbert_f1_macro" ..\stage2_training\logs\exp4_test.log
    findstr /C:"test_report_radgraph_f1" ..\stage2_training\logs\exp4_test.log
) else (
    echo [%TIME%] ERROR: Experiment 4 testing failed - check logs\exp4_test.log
    pause
    exit /b 1
)

echo.
echo ========================================
echo ALL TESTING COMPLETE!
echo ========================================
echo.
echo Next step: Run python extract_results.py to summarize all results
echo.
pause
