@echo off
REM ============================================================================
REM Automated BenchX SHARP Test
REM ============================================================================

echo ========================================
echo   BenchX SHARP Automated Test
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote

REM ============================================================================
REM Step 1: Pull latest code
REM ============================================================================
echo [1/5] Pulling latest code from GitHub...
git pull origin main
echo.

REM ============================================================================
REM Step 2: Fix the include line (convirt -> mgca_vit)
REM ============================================================================
echo [2/5] Fixing include line in sharp_siim_final.yml...
echo.

REM Create corrected version with mgca_vit include
powershell -Command "(Get-Content sharp_siim_final.yml) -replace 'configs/_base_/models/convirt.yml', 'configs/_base_/models/mgca_vit.yml' | Set-Content sharp_siim_final_fixed.yml"

echo Fixed config created: sharp_siim_final_fixed.yml
echo.

REM ============================================================================
REM Step 3: Copy to BenchX
REM ============================================================================
echo [3/5] Copying fixed config to BenchX...
copy sharp_siim_final_fixed.yml BenchX\configs\classification\SIIM\sharp.yml /Y

if errorlevel 1 (
    echo [ERROR] Failed to copy config!
    pause
    exit /b 1
)

echo [OK] Config copied
echo.

REM ============================================================================
REM Step 4: Run training and capture output
REM ============================================================================
echo [4/5] Running BenchX training...
echo   This will either work or show the next error to fix
echo.

cd BenchX

python bin/train.py configs/classification/SIIM/sharp.yml 2>&1 | tee ..\benchx_test_output.txt

set TRAIN_EXIT_CODE=%ERRORLEVEL%

cd ..

REM ============================================================================
REM Step 5: Analyze results
REM ============================================================================
echo.
echo ========================================
echo [5/5] Test Results
echo ========================================
echo.

if %TRAIN_EXIT_CODE% == 0 (
    echo ✅ SUCCESS! Training started without errors!
    echo.
    echo Check BenchX\experiments\classification\siim\ for results
) else (
    echo ❌ Training failed - analyzing error...
    echo.
    echo Full output saved to: benchx_test_output.txt
    echo.
    echo Last 30 lines of output:
    echo ----------------------------------------
    powershell -Command "Get-Content benchx_test_output.txt | Select-Object -Last 30"
    echo ----------------------------------------
    echo.

    REM Check for specific error types
    findstr /C:"NameError" benchx_test_output.txt >nul
    if not errorlevel 1 (
        echo 🔍 Detected: NameError - function/class not defined
        echo    Likely: Missing import in base config
    )

    findstr /C:"KeyError" benchx_test_output.txt >nul
    if not errorlevel 1 (
        echo 🔍 Detected: KeyError - missing key in checkpoint
        echo    Likely: Checkpoint key mismatch
    )

    findstr /C:"RuntimeError" benchx_test_output.txt >nul
    if not errorlevel 1 (
        echo 🔍 Detected: RuntimeError
        findstr /C:"size mismatch" benchx_test_output.txt >nul
        if not errorlevel 1 (
            echo    Likely: Model architecture mismatch
        )
    )

    findstr /C:"TypeError" benchx_test_output.txt >nul
    if not errorlevel 1 (
        echo 🔍 Detected: TypeError - unexpected argument
        echo    Likely: Config parameter not supported by model
    )
)

echo.
echo ========================================
echo   Next Steps
echo ========================================
echo.

if %TRAIN_EXIT_CODE% == 0 (
    echo Training is running! Let it complete.
    echo Results will be in: BenchX\experiments\classification\siim\
) else (
    echo Send me the output above or the file:
    echo   C:\Users\aya.alaswad\remote\benchx_test_output.txt
    echo.
    echo I'll create a fix based on the error type.
)

echo.
pause
