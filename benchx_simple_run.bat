@echo off
REM ============================================================================
REM BenchX Simple Runner - Skip Setup, Just Run
REM ============================================================================
REM
REM Assumes:
REM   - BenchX already cloned
REM   - PyTorch already installed (you have it from SHARP)
REM   - Just need to fix requirements and run
REM ============================================================================

echo ========================================
echo   BenchX Simple Runner
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote\BenchX

REM Install only missing packages (PyTorch already installed)
echo [1/4] Installing missing packages...
pip install transformers==4.30.0 timm albumentations scikit-learn -q

echo [OK] Packages installed
echo.

REM Copy SHARP model
echo [2/4] Installing SHARP...
copy /Y ..\MyReasearch\benchx_sharp_model.py models\sharp.py

REM Create config directories
mkdir configs\classification\siim 2>nul
mkdir configs\classification\rsna 2>nul
mkdir configs\classification\nih 2>nul
mkdir configs\classification\vindr 2>nul

REM Copy configs
copy /Y ..\MyReasearch\benchx_config_*.yml configs\classification\

echo [OK] SHARP integrated
echo.

REM Test SHARP
echo [3/4] Testing SHARP...
python -c "from models.sharp import SHARP; print('[OK] SHARP imports')"

if errorlevel 1 (
    echo [ERROR] SHARP test failed!
    pause
    exit /b 1
)

echo [OK] SHARP works
echo.

REM Check datasets
echo [4/4] Checking datasets...
set FOUND=0

if exist "D:\datasets\siim-pneumothorax\" (
    echo [OK] SIIM found
    set FOUND=1
)
if exist "D:\datasets\rsna-pneumonia\" (
    echo [OK] RSNA found
    set FOUND=1
)
if exist "D:\datasets\vindr-cxr\" (
    echo [OK] VinDr found
    set FOUND=1
)
if exist "D:\datasets\nih-chestxray14\" (
    echo [OK] NIH found
    set FOUND=1
)

if %FOUND%==0 (
    echo.
    echo [WARNING] No datasets found!
    echo Download at least SIIM first.
    echo See: benchx_download_data.md
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Ready to Run!
echo ========================================
echo.
echo Run training with:
echo   python bin/train.py configs/classification/siim/sharp.yml
echo.
pause
