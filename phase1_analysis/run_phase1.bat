@echo off
REM Phase 1: t-SNE/UMAP Analysis on Stage 1 Encoders
REM
REM This script runs the complete Phase 1 analysis pipeline:
REM   1. Extract embeddings from all 4 Stage 1 checkpoints
REM   2. Visualize with t-SNE and UMAP
REM   3. Compute concept consistency @ top-5 metric
REM
REM Can run in parallel with Exp #2b (no GPU conflict - uses inference only)

echo ============================================================================
echo Phase 1: Stage 1 Encoder Analysis (t-SNE/UMAP + Concept Consistency)
echo ============================================================================
echo.
echo This will:
echo   1. Extract embeddings from 4 Stage 1 checkpoints (Exp 1-4)
echo   2. Create t-SNE and UMAP visualizations
echo   3. Compute concept consistency @ top-5 metric
echo.
echo Expected runtime: ~30-60 minutes (inference only, minimal GPU usage)
echo.
pause

REM Step 1: Extract embeddings
echo.
echo ============================================================================
echo Step 1/3: Extracting embeddings from Stage 1 checkpoints
echo ============================================================================
echo.

python extract_embeddings.py ^
  --scene_dir D:\datasets\mimic-ext-cxr-qba\scene_graphs\scene_data ^
  --image_dir D:\datasets\mimic-cxr-jpg ^
  --split_csv D:\datasets\mimic-cxr-jpg\mimic-cxr-2.0.0-split.csv.gz ^
  --output_dir embeddings ^
  --max_samples 5000 ^
  --device cuda

if errorlevel 1 (
    echo.
    echo ERROR: Embedding extraction failed!
    pause
    exit /b 1
)

REM Step 2: Visualize with t-SNE and UMAP
echo.
echo ============================================================================
echo Step 2/3: Creating t-SNE and UMAP visualizations
echo ============================================================================
echo.

REM Visualize by entity (most informative)
python visualize_embeddings.py ^
  --embedding_dir embeddings ^
  --output_dir figures ^
  --method both ^
  --color_by entity

if errorlevel 1 (
    echo.
    echo ERROR: Visualization failed!
    pause
    exit /b 1
)

REM Also create visualizations by polarity (shows pos/neg distinction)
python visualize_embeddings.py ^
  --embedding_dir embeddings ^
  --output_dir figures ^
  --method both ^
  --color_by polarity

if errorlevel 1 (
    echo.
    echo WARNING: Polarity visualization failed (continuing...)
)

REM Step 3: Compute concept consistency
echo.
echo ============================================================================
echo Step 3/3: Computing concept consistency @ top-5
echo ============================================================================
echo.

python concept_consistency_probe.py ^
  --embedding_dir embeddings ^
  --output_dir consistency ^
  --k 5

if errorlevel 1 (
    echo.
    echo ERROR: Consistency analysis failed!
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Phase 1 Complete!
echo ============================================================================
echo.
echo Results saved to:
echo   - Embeddings:    embeddings\
echo   - Figures:       figures\
echo   - Consistency:   consistency\
echo.
echo Key outputs:
echo   - stage1_comparison_tsne_entity.png
echo   - stage1_comparison_umap_entity.png
echo   - concept_consistency_k5.json
echo.
pause
