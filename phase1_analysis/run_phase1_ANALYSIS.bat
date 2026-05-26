@echo off
REM Phase 1 Analysis: Proper Geometry Metrics
REM
REM This runs the CORRECT Phase 1 analysis:
REM 1. Cosine similarity distributions (positive vs negative pairs)
REM 2. Alignment + uniformity metrics (Wang & Isola 2020)
REM 3. UMAP for Exp #2 collapse ONLY
REM
REM These are rigorous, quantitative metrics that directly explain R@1 performance.
REM DO NOT use UMAP "tight clusters" claims for other experiments.

echo ============================================================================
echo Phase 1 Analysis: Rigorous Geometry Metrics
echo ============================================================================
echo.
echo This will compute:
echo   1. Cosine similarity distributions (positive vs negative pairs)
echo   2. Alignment and uniformity (Wang and Isola 2020)
echo   3. UMAP visualization for Exp #2 collapse ONLY
echo.
echo These metrics are:
echo   - Quantitative (not subjective UMAP interpretations)
echo   - Theoretically grounded
echo   - Directly explain retrieval performance
echo.
pause

echo.
echo ============================================================================
echo Step 1: Cosine Similarity Distributions
echo ============================================================================
python compute_cosine_similarity.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Cosine similarity analysis failed
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Step 2: Alignment and Uniformity Metrics
echo ============================================================================
python compute_alignment_uniformity.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Alignment/uniformity analysis failed
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Step 3: UMAP for Exp #2 Collapse (Evidence Only)
echo ============================================================================
python plot_exp2_collapse_UMAP.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: UMAP plotting failed
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Phase 1 Analysis Complete!
echo ============================================================================
echo.
echo Results saved to plots/:
echo   - cosine_similarity_distributions.png
echo   - cosine_similarity_stats.txt
echo   - alignment_uniformity.png
echo   - alignment_uniformity_metrics.txt
echo   - exp2_collapse_umap.png
echo.
echo Use these for your rebuttal instead of subjective UMAP claims!
echo.
pause
