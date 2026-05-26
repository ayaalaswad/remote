@echo off
REM Verify all paths needed for Stage 2 training before starting
REM Run this on REMOTE DESKTOP

echo ========================================
echo Stage 2 Training - Path Verification
echo ========================================
echo.

cd /d C:\Users\aya.alaswad\remote\cxrmate

echo Checking CRITICAL paths that could cause crashes:
echo.

REM 1. CheXbert checkpoint (for validation)
echo [1] CheXbert checkpoint (for validation):
if exist "checkpoints\stanford\chexbert\chexbert.pth" (
    echo     ✓ checkpoints\stanford\chexbert\chexbert.pth
    for %%A in ("checkpoints\stanford\chexbert\chexbert.pth") do echo       Size: %%~zA bytes
) else (
    echo     ✗ MISSING: checkpoints\stanford\chexbert\chexbert.pth
    echo       Training will crash during validation!
)
echo.

REM 2. Stage 1 ViT checkpoints (pre-trained models for Stage 2)
echo [2] Stage 1 ViT checkpoints (required at training start):
echo     Exp #1 baseline needs:
if exist "D:\experiments\exp1_baseline\p3_best.pt" (
    echo     ✓ D:\experiments\exp1_baseline\p3_best.pt
    for %%A in ("D:\experiments\exp1_baseline\p3_best.pt") do echo       Size: %%~zA bytes
) else (
    echo     ✗ MISSING: D:\experiments\exp1_baseline\p3_best.pt
    echo       Exp #1 training will crash at initialization!
)
echo.

echo     Exp #3 full needs:
if exist "D:\experiments\exp3_full_sharp\p3_best.pt" (
    echo     ✓ D:\experiments\exp3_full_sharp\p3_best.pt
    for %%A in ("D:\experiments\exp3_full_sharp\p3_best.pt") do echo       Size: %%~zA bytes
) else (
    echo     ✗ MISSING: D:\experiments\exp3_full_sharp\p3_best.pt
    echo       Exp #3 training will crash at initialization!
)
echo.

REM 3. Dataset CSV files
echo [3] Dataset CSV files (required for data loading):
if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-split.csv.gz" (
    echo     ✓ mimic-cxr-2.0.0-split.csv.gz
) else (
    echo     ✗ MISSING: mimic-cxr-2.0.0-split.csv.gz
)

if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic-cxr-2.0.0-metadata.csv.gz" (
    echo     ✓ mimic-cxr-2.0.0-metadata.csv.gz
) else (
    echo     ✗ MISSING: mimic-cxr-2.0.0-metadata.csv.gz
)

if exist "D:\datasets\physionet.org\files\mimic-cxr-jpg\2.0.0\mimic_cxr_sections\mimic_cxr_sectioned.csv" (
    echo     ✓ mimic_cxr_sections\mimic_cxr_sectioned.csv
) else (
    echo     ✗ MISSING: mimic_cxr_sections\mimic_cxr_sectioned.csv
)
echo.

REM 4. Output directories (will be created automatically, but good to check)
echo [4] Output directories (created automatically if missing):
if exist "experiments" (
    echo     ✓ experiments directory exists
) else (
    echo     ⚠ experiments directory will be created
)
echo.

echo ========================================
echo Summary
echo ========================================
echo.
echo If you see any ✗ MISSING errors above, DO NOT start training!
echo Those paths must exist or training will crash.
echo.
echo The most common missing file is the Stage 1 ViT checkpoint.
echo Make sure Stage 1 training completed and saved p3_best.pt
echo.

pause
