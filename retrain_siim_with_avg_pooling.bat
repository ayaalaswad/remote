@echo off
REM ============================================================================
REM Retrain SIIM with FIXED global_pool: avg (was token)
REM This should dramatically improve F1 scores
REM ============================================================================

echo ========================================
echo   SIIM Retrain - Fixed global_pool
echo ========================================
echo.
echo BEFORE: global_pool = token, F1 = 0-2.35%%
echo AFTER:  global_pool = avg,   F1 = Expected 15-45%%
echo.

cd C:\Users\aya.alaswad\remote

REM ============================================================================
REM STEP 1: VERIFY FIX
REM ============================================================================

echo [1/3] Verifying configs have global_pool: avg...
echo.

findstr /C:"global_pool: avg" sharp_siim_1pct.yml >nul
if errorlevel 1 (
    echo [ERROR] sharp_siim_1pct.yml still has global_pool: token!
    echo Pull latest changes: git pull origin main
    pause
    exit /b 1
)

findstr /C:"global_pool: avg" sharp_siim_10pct.yml >nul
if errorlevel 1 (
    echo [ERROR] sharp_siim_10pct.yml still has global_pool: token!
    echo Pull latest changes: git pull origin main
    pause
    exit /b 1
)

findstr /C:"global_pool: avg" sharp_siim_100pct.yml >nul
if errorlevel 1 (
    echo [ERROR] sharp_siim_100pct.yml still has global_pool: token!
    echo Pull latest changes: git pull origin main
    pause
    exit /b 1
)

echo [OK] All configs verified to use global_pool: avg
echo.

REM ============================================================================
REM STEP 2: CLEAN OLD RESULTS (OPTIONAL)
REM ============================================================================

echo [2/3] Clean old results with token pooling?
echo.
echo This will DELETE old SIIM training results (F1 0-2.35%%)
echo.
choice /C YN /M "Delete old results and start fresh"

if errorlevel 2 (
    echo [SKIP] Keeping old results (training will overwrite)
    echo.
) else (
    echo [CLEAN] Removing old SIIM results...

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

    echo [OK] Old results cleaned
    echo.
)

REM ============================================================================
REM STEP 3: RETRAIN ALL 3 SPLITS
REM ============================================================================

echo [3/3] Ready to retrain SIIM with avg pooling
echo.
echo Training order: 1%% (~30 min) -> 10%% (~1 hr) -> 100%% (~2-4 hrs)
echo Total time: 3-6 hours
echo.
echo Press any key to start training, or Ctrl+C to cancel...
pause >nul

cd BenchX

REM ---------- SIIM 1% ----------
echo.
echo ========================================
echo   Training SIIM 1%% (avg pooling)
echo ========================================
echo Started at %time%
echo.

python bin/train.py ../sharp_siim_1pct.yml

if errorlevel 1 (
    echo.
    echo [ERROR] SIIM 1%% training failed!
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
echo   Training SIIM 10%% (avg pooling)
echo ========================================
echo Started at %time%
echo.

python bin/train.py ../sharp_siim_10pct.yml

if errorlevel 1 (
    echo.
    echo [ERROR] SIIM 10%% training failed!
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
echo   Training SIIM 100%% (avg pooling)
echo ========================================
echo Started at %time%
echo.

python bin/train.py ../sharp_siim_100pct.yml

if errorlevel 1 (
    echo.
    echo [ERROR] SIIM 100%% training failed!
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
echo   TRAINING COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Run: python calculate_siim_new_f1.py
echo 2. Compare NEW F1 scores with OLD:
echo      OLD (token): 0%%, 0.8%%, 2.35%%
echo      NEW (avg):   Expected 15-45%%
echo 3. If improved, run: push_siim_results.bat
echo.

pause
