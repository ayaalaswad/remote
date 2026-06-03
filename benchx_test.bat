@echo off
REM ============================================================================
REM BenchX Quick Test: Verify SHARP integration works
REM ============================================================================
REM
REM This tests:
REM   1. Conda environment exists
REM   2. SHARP model loads
REM   3. Forward pass works
REM
REM Runtime: 1 minute
REM ============================================================================

echo ========================================
echo   BenchX Quick Test
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote\BenchX

REM Activate conda environment
echo [1/3] Activating conda environment...
call conda activate benchx
if errorlevel 1 (
    echo [ERROR] Conda environment 'benchx' not found!
    echo Run: benchx_setup.bat
    pause
    exit /b 1
)
echo    OK: benchx environment active

REM Test SHARP model import
echo.
echo [2/3] Testing SHARP model import...
python -c "from models.sharp import SHARP; print('   OK: SHARP model imported')" 2>nul
if errorlevel 1 (
    echo [ERROR] SHARP model not found!
    echo Run: benchx_integrate_sharp.bat
    pause
    exit /b 1
)

REM Test SHARP model loading
echo.
echo [3/3] Testing SHARP checkpoint loading...
python -c "import torch; from models.sharp import SHARP; model = SHARP('D:/experiments/exp3_hardneg/p3_best.pt', num_classes=2); x = torch.randn(2, 3, 224, 224); y = model(x); print(f'   OK: SHARP forward pass (input: {x.shape}, output: {y.shape})')" 2>nul
if errorlevel 1 (
    echo [ERROR] SHARP checkpoint loading failed!
    echo Check: D:\experiments\exp3_hardneg\p3_best.pt exists
    pause
    exit /b 1
)

echo.
echo ========================================
echo   All Tests Passed!
echo ========================================
echo.
echo SHARP is ready for BenchX evaluation.
echo.
echo Next steps:
echo   1. Download datasets (see: benchx_download_data.md)
echo   2. Run evaluation: benchx_run_all.bat
echo.
pause
