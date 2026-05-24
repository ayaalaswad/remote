@echo off
REM Phase 1 - FIXED VERSION with debug output

echo ============================================================================
echo Phase 1: Extract Embeddings (FIXED - with debug output)
echo ============================================================================
echo.
pause

python extract_embeddings_FIXED.py ^
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data ^
  --image_dir D:\datasets\mimic-cxr-jpg ^
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz ^
  --output_dir embeddings ^
  --max_samples 5000 ^
  --device cuda

pause
