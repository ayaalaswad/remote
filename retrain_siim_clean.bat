@echo off
REM ============================================================================
REM Clean SIIM Retrain - Verifies everything before training
REM ============================================================================

echo ========================================
echo   SIIM Clean Retrain
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote

REM ============================================================================
REM STEP 1: VERIFY SPLITS ARE FIXED
REM ============================================================================

echo [1/4] Verifying SIIM splits are fixed...
echo.

python -c "import pandas as pd; df = pd.read_csv('BenchX/datasets/SIIM/siim_labels.csv'); val_df = df[df['split']=='val']; n_pos = (val_df['has_pneumo']==1).sum(); print(f'Validation positives: {n_pos}'); exit(0 if n_pos > 0 else 1)"

if errorlevel 1 (
    echo.
    echo [ERROR] Splits are not fixed! Validation has no positives.
    echo Run: python fix_siim_complete.py
    pause
    exit /b 1
)

echo [OK] Splits are fixed!
echo.

REM ============================================================================
REM STEP 2: VERIFY CONFIG FILES EXIST
REM ============================================================================

echo [2/4] Verifying config files exist...
echo.

if not exist "sharp_siim_1pct.yml" (
    echo [ERROR] sharp_siim_1pct.yml not found!
    pause
    exit /b 1
)
echo [OK] sharp_siim_1pct.yml found

if not exist "sharp_siim_10pct.yml" (
    echo [ERROR] sharp_siim_10pct.yml not found!
    pause
    exit /b 1
)
echo [OK] sharp_siim_10pct.yml found

if not exist "sharp_siim_100pct.yml" (
    echo [ERROR] sharp_siim_100pct.yml not found!
    pause
    exit /b 1
)
echo [OK] sharp_siim_100pct.yml found

echo.

REM ============================================================================
REM STEP 3: CLEAN OLD INCOMPLETE RUNS (OPTIONAL)
REM ============================================================================

echo [3/4] Clean old incomplete training directories?
echo.
echo This will DELETE any existing incomplete SIIM training results.
echo Only do this if you want to start completely fresh.
echo.
choice /C YN /M "Delete old SIIM training directories"

if errorlevel 2 (
    echo [SKIP] Keeping existing directories
    echo.
) else (
    echo [CLEAN] Removing old training directories...

    if exist "BenchX\experiments\classification\siim\SHARP_1pct" (
        rmdir /s /q "BenchX\experiments\classification\siim\SHARP_1pct"
        echo   - Removed SHARP_1pct
    )

    if exist "BenchX\experiments\classification\siim\SHARP_10pct" (
        rmdir /s /q "BenchX\experiments\classification\siim\SHARP_10pct"
        echo   - Removed SHARP_10pct
    )

    if exist "BenchX\experiments\classification\siim\SHARP_100pct" (
        rmdir /s /q "BenchX\experiments\classification\siim\SHARP_100pct"
        echo   - Removed SHARP_100pct
    )

    echo [OK] Cleaned old directories
    echo.
)

REM ============================================================================
REM STEP 4: START TRAINING
REM ============================================================================

echo [4/4] Ready to start training!
echo.
echo This will train 3 experiments sequentially (3-6 hours total):
echo   1. SIIM 1%%   (~30 min)
echo   2. SIIM 10%%  (~1 hour)
echo   3. SIIM 100%% (~2-4 hours)
echo.
echo Press any key to start, or Ctrl+C to cancel...
pause >nul

cd BenchX

REM ---------- SIIM 1% ----------
echo.
echo ========================================
echo   Training SIIM 1%%
echo ========================================
echo Started at %time%
echo.

python bin/train.py ../sharp_siim_1pct.yml

if errorlevel 1 (
    echo.
    echo [ERROR] SIIM 1%% training failed!
    echo Check the error above.
    cd ..
    pause
    exit /b 1
)

echo.
echo [OK] SIIM 1%% completed at %time%
echo.

REM ---------- SIIM 10% ----------
echo.
echo ========================================
echo   Training SIIM 10%%
echo ========================================
echo Started at %time%
echo.

python bin/train.py ../sharp_siim_10pct.yml

if errorlevel 1 (
    echo.
    echo [ERROR] SIIM 10%% training failed!
    echo Check the error above.
    cd ..
    pause
    exit /b 1
)

echo.
echo [OK] SIIM 10%% completed at %time%
echo.

REM ---------- SIIM 100% ----------
echo.
echo ========================================
echo   Training SIIM 100%%
echo ========================================
echo Started at %time%
echo.

python bin/train.py ../sharp_siim_100pct.yml

if errorlevel 1 (
    echo.
    echo [ERROR] SIIM 100%% training failed!
    echo Check the error above.
    cd ..
    pause
    exit /b 1
)

echo.
echo [OK] SIIM 100%% completed at %time%
echo.

cd ..

REM ============================================================================
REM COMPLETE
REM ============================================================================

echo.
echo ========================================
echo   ALL TRAINING COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Run: python calculate_f1_from_pushed_results.py
echo 2. Check F1 scores are reasonable (not 0%%)
echo 3. Run: push_siim_results.bat
echo.

pause
