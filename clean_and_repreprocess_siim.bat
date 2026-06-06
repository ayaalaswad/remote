@echo off
REM ============================================================================
REM Clean SIIM Dataset and Use BenchX's Original Preprocessing
REM ============================================================================

echo ========================================
echo   SIIM Dataset - Clean Repreprocessing
echo ========================================
echo.
echo This will:
echo   1. Backup broken SIIM dataset
echo   2. Download correct Kaggle dataset (if needed)
echo   3. Use BenchX's original preprocessing script
echo.
echo ========================================
echo.

cd C:\Users\aya.alaswad\remote

REM ============================================================================
REM Step 1: Backup current broken dataset
REM ============================================================================
echo [1/3] Backing up current SIIM dataset...

if exist BenchX\datasets\SIIM_BACKUP (
    echo   Backup already exists, skipping...
) else (
    if exist BenchX\datasets\SIIM (
        move BenchX\datasets\SIIM BenchX\datasets\SIIM_BACKUP
        echo   ✓ Backed up to SIIM_BACKUP
    )
)

echo.

REM ============================================================================
REM Step 2: Check for correct Kaggle dataset
REM ============================================================================
echo [2/3] Checking for correct SIIM dataset...
echo.
echo BenchX expects the Kaggle dataset:
echo   "pneumothorax-chest-xray-images-and-masks"
echo   https://www.kaggle.com/datasets/vbookshelf/pneumothorax-chest-xray-images-and-masks
echo.
echo This dataset has:
echo   - png_images/ (already converted PNG files)
echo   - png_masks/ (segmentation masks)
echo   - stage_1_train_images.csv
echo   - stage_1_test_images.csv
echo.
echo You currently have stage_2 DICOM data, which is different.
echo.

set /p DOWNLOAD="Do you want instructions to download the correct dataset? (y/n): "

if /i "%DOWNLOAD%"=="y" (
    echo.
    echo ========================================
    echo   Download Instructions
    echo ========================================
    echo.
    echo 1. Go to: https://www.kaggle.com/datasets/vbookshelf/pneumothorax-chest-xray-images-and-masks
    echo 2. Click "Download" (you'll need a Kaggle account)
    echo 3. Extract to: D:\datasets\siim-png\
    echo 4. Re-run this script
    echo.
    echo After downloading, set these paths:
    echo   - data_path: D:\datasets\siim-png\
    echo   - processed_datapath: C:\Users\aya.alaswad\remote\BenchX\datasets\SIIM\
    echo.
    pause
    exit /b 0
)

REM ============================================================================
REM Step 3: Alternative - Use what we have with proper mapping
REM ============================================================================
echo.
echo [3/3] Alternative: Skip SIIM, use RSNA instead
echo.
echo SIIM dataset mapping is complex (DICOM UIDs vs ImageIds).
echo.
echo RSNA dataset is simpler and already downloaded.
echo Would you like to:
echo   A. Skip SIIM and run RSNA directly
echo   B. Download correct SIIM dataset and come back
echo.

set /p CHOICE="Choice (A/B): "

if /i "%CHOICE%"=="A" (
    echo.
    echo Proceeding with RSNA only...
    echo See: run_benchx_rsna.bat
    echo.
) else (
    echo.
    echo Download the dataset and re-run this script.
    echo.
)

pause
