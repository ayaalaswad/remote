@echo off
REM ============================================================================
REM BenchX Setup Fix - No Conda, Fixed Requirements
REM ============================================================================

echo ========================================
echo   BenchX Setup (Pip Only)
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote\BenchX

REM Fix requirements.txt (BenchX has wrong versions)
echo [1/3] Fixing requirements.txt...
(
echo torch==2.1.2
echo torchvision==0.16.2
echo transformers==4.30.0
echo timm==0.9.2
echo albumentations==1.3.0
echo opencv-python==4.8.0.76
echo pandas
echo numpy
echo scipy
echo scikit-learn
echo tqdm
echo tensorboard
echo pillow
echo matplotlib
echo pyyaml
) > requirements_fixed.txt

echo [OK] Fixed requirements saved

REM Install dependencies with pip
echo.
echo [2/3] Installing dependencies...
pip install -r requirements_fixed.txt

if errorlevel 1 (
    echo [ERROR] Installation failed!
    pause
    exit /b 1
)

echo [OK] Dependencies installed

REM Test imports
echo.
echo [3/3] Testing imports...
python -c "import torch; import transformers; import timm; print('[OK] All packages imported successfully')"

if errorlevel 1 (
    echo [ERROR] Import test failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo BenchX is ready (using pip, no conda)
echo.
pause
