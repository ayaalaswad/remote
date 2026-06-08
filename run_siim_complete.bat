@echo off
echo ============================================================
echo SIIM Complete Pipeline - Preprocessing + Training (All Splits)
echo ============================================================
echo.

REM Activate conda environment
call conda activate benchx
cd C:\Users\aya.alaswad\remote

echo Step 1: Running SIIM preprocessing (CSV-based labels only)...
echo.
python preprocess_siim_csv_only.py
if errorlevel 1 (
    echo ERROR: SIIM preprocessing failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Preprocessing complete! Starting training...
echo ============================================================
echo.

REM Copy configs from git repo to BenchX
if not exist "BenchX\configs\classification\SIIM" mkdir "BenchX\configs\classification\SIIM"
copy sharp_siim_1pct.yml BenchX\configs\classification\SIIM\sharp_siim_1pct.yml /Y
copy sharp_siim_10pct.yml BenchX\configs\classification\SIIM\sharp_siim_10pct.yml /Y
copy sharp_siim_100pct.yml BenchX\configs\classification\SIIM\sharp_siim_100pct.yml /Y

echo Step 2: Training SIIM 1%%...
cd BenchX
python bin/train.py configs/classification/SIIM/sharp_siim_1pct.yml
if errorlevel 1 (
    echo WARNING: SIIM 1%% training failed!
)

echo.
echo Step 3: Training SIIM 10%%...
python bin/train.py configs/classification/SIIM/sharp_siim_10pct.yml
if errorlevel 1 (
    echo WARNING: SIIM 10%% training failed!
)

echo.
echo Step 4: Training SIIM 100%%...
python bin/train.py configs/classification/SIIM/sharp_siim_100pct.yml
if errorlevel 1 (
    echo WARNING: SIIM 100%% training failed!
)

echo.
echo ============================================================
echo SIIM Complete Pipeline Finished!
echo Results in: BenchX\experiments\classification\siim\
echo ============================================================
pause
