@echo off
REM Phase 1 - SIMPLE STANDALONE VERSION
REM This will work because it has ZERO dependencies on the training script

echo ============================================================================
echo Phase 1: Extract Embeddings (STANDALONE VERSION)
echo ============================================================================
echo.
echo This version is SELF-CONTAINED - no import dependencies!
echo.
echo Expected runtime: ~30-60 minutes
echo.
pause

echo.
echo Extracting embeddings from all checkpoints...
echo.

python extract_embeddings_SIMPLE.py ^
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data ^
  --image_dir D:\datasets\mimic-cxr-jpg ^
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz ^
  --output_dir embeddings ^
  --max_samples 5000 ^
  --device cuda

if errorlevel 1 (
    echo.
    echo ERROR: Extraction failed!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo SUCCESS! Embeddings extracted
echo ============================================================================
echo.
echo Saved to: embeddings\
echo   - exp1_embeddings.npz
echo   - exp2_embeddings.npz
echo   - exp3_embeddings.npz
echo   - exp4_embeddings.npz
echo.
pause
