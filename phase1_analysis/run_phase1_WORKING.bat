@echo off
REM Phase 1 - WORKING VERSION
REM Fixed: Uses patient_id + study_id from scene graphs

echo ============================================================================
echo Phase 1: Extract Embeddings (WORKING - uses patient_id + study_id)
echo ============================================================================
echo.
echo Reduced to 1000 samples for faster testing (increase to 5000 if it works)
echo.
pause

python extract_embeddings_WORKING.py ^
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data ^
  --image_dir D:\datasets\mimic-cxr-jpg ^
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz ^
  --output_dir embeddings ^
  --max_samples 1000 ^
  --device cuda

echo.
if errorlevel 1 (
    echo ERROR: Extraction failed
) else (
    echo SUCCESS! Check embeddings/ directory
)
pause
