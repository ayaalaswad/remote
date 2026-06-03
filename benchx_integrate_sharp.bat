@echo off
REM ============================================================================
REM BenchX Setup - Step 2: Integrate SHARP model into BenchX
REM ============================================================================

echo ========================================
echo   Integrating SHARP into BenchX
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote

REM Check if BenchX exists
if not exist "BenchX\" (
    echo [ERROR] BenchX not found! Run benchx_setup.bat first.
    pause
    exit /b 1
)

REM Copy SHARP model wrapper into BenchX
echo [1/2] Copying SHARP model wrapper...
copy /Y MyReasearch\benchx_sharp_model.py BenchX\models\sharp.py
if errorlevel 1 (
    echo [ERROR] Failed to copy SHARP model
    pause
    exit /b 1
)
echo    OK: BenchX\models\sharp.py

REM Create config directory for SHARP
echo.
echo [2/2] Creating SHARP config templates...

mkdir BenchX\configs\classification\rsna 2>nul
mkdir BenchX\configs\classification\siim 2>nul
mkdir BenchX\configs\classification\nih 2>nul
mkdir BenchX\configs\classification\vindr 2>nul

REM Copy template configs from MyReasearch
copy /Y MyReasearch\benchx_config_rsna.yml BenchX\configs\classification\rsna\sharp.yml 2>nul
copy /Y MyReasearch\benchx_config_siim.yml BenchX\configs\classification\siim\sharp.yml 2>nul
copy /Y MyReasearch\benchx_config_nih.yml BenchX\configs\classification\nih\sharp.yml 2>nul
copy /Y MyReasearch\benchx_config_vindr.yml BenchX\configs\classification\vindr\sharp.yml 2>nul

echo.
echo ========================================
echo   Integration Complete!
echo ========================================
echo.
echo SHARP model installed at: BenchX\models\sharp.py
echo Config files ready in: BenchX\configs\classification\
echo.
echo Next: Download datasets or run quick test
echo   Test: cd BenchX ^&^& python -c "from models.sharp import SHARP; print('OK')"
echo.
pause
